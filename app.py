from dotenv import load_dotenv
import os
from flask import Flask,request
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import time
import requests as rq
import json

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

def send_push_notification(notification_data):
    url = f"https://ntfy.sh/{os.getenv('ntfy_topic')}"
    rq.post(url, json=notification_data)

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

@app.route("/",methods=['GET', 'POST'])
def home_page():
    #check if header has "type:form"
    #if it does, then it is a form submission
    if request.headers.get('type') is None:
        #return the last 10 documents from the database according to timestamp
        return f"{list(db['forms'].find().sort('timestamp',-1).limit(10))}"
    if request.headers.get('type') == 'form':
        #get the form data
        form_data = request.json
        #push raw data to the database
        result = db['raw'].insert_one(form_data)
        
        send_push_notification(f"New form submission from {form_data['filledby']}\nForms Data: {json.dumps(form_data)}")
        
        #process the data
        processed_data = process_data(form_data)
        #insert the form data to the database
        result = db['processed'].insert_one(processed_data)
        
        return f"{result}"
    
    
if __name__ == "__main__":
    app.run(debug=True)