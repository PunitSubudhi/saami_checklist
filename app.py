from dotenv import load_dotenv
import os
from flask import Flask,request
from zoho_oauth2 import ZohoAPITokens
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import time

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
        #Parse timestamp from form data and add it to the form data
        form_data['timestamp'] = time.time()
        print(form_data)
        #insert the form data to the database
        result = db['forms'].insert_one(form_data)
        
        return f"{result}"
    
    
    