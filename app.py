from dotenv import load_dotenv
import os
from flask import Flask, request, render_template, redirect
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import time
import requests as rq

load_dotenv()

app = Flask(__name__)
uri = f"mongodb+srv://{os.getenv('db_username')}:{os.getenv('db_password')}@{os.getenv('mongo_uri')}/?retryWrites=true&w=majority&appName=tasks"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['forms']

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

def root_dir():
    return os.path.abspath(os.path.dirname(__file__))

def send_push_notification(notification_data):
    try:
        url = f"https://ntfy.sh/{os.getenv('ntfy_topic')}"
        resp = rq.post(url, data=notification_data)
        return json.dumps(resp.json())
    except Exception as e:
        db['errors'].insert_one({"error": str(e)})
        return str(e)

def process_data(data):
    processed_data = {}
    processed_data['timestamp'] = time.time()
    return processed_data

'''
api_tokens = ZohoAPITokens(
    client_id=os.getenv('client_id'),
    client_secret=os.getenv('client_secret'),
    refresh_token=os.getenv('refresh_token'),
    redirect_uri=os.getenv('redirect_uri')
)
'''

@app.route("/", methods=['GET', 'POST'])
def home_page():
    # check if header has "type:form"
    # if it does, then it is a form submission
    if request.headers.get('type') is None:
        # return the last 10 documents from the database according to timestamp
        #return f"{list(db['forms'].find().sort('timestamp', 1).limit(10))}"
        return redirect(os.getenv("redirect_url"), code=302)
    elif request.headers.get('type') == 'form':
        # get the form data
        form_data = request.json
        # push raw data to the database
        result = db['raw'].insert_one(form_data)
        
        if form_data['filledby'] is not None:
            send_push_notification(f"New form submission from {form_data['filledby']}\nForms Data: \n{(form_data)}")
        else:
            send_push_notification(f"New form submission\nForms Data: \n{(form_data)}")    
        
        # process the data
        processed_data = process_data(form_data)
        # insert the form data to the database
        result = db['processed'].insert_one(processed_data)
        
        return f"{result}"
    elif request.headers.get('type') == 'push':
        notification_data = request.data
        response = send_push_notification(notification_data)
        return response
    elif request.headers.get('type') == 'get':
        return f"{list(db['raw'].find().sort('timestamp', 1).limit(10))}"

@app.route("/forms", methods=['GET'])
def get_forms():
    return f"{list(db['raw'].find().sort('timestamp', 1).limit(10))}"

if __name__ == "__main__":
    app.run()
