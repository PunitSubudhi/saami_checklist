from dotenv import load_dotenv
import os
from flask import Flask
from flask_pymongo import PyMongo
from zoho_oauth2 import ZohoAPITokens

load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = f"mongodb+srv://{os.getenv('db_username')}:{os.getenv('db_password')}@{os.getenv('mongo_uri')}/?retryWrites=true&w=majority&appName=tasks"
mongo = PyMongo(app)
api_tokens = ZohoAPITokens(
    client_id=os.getenv('client_id'),
    client_secret=os.getenv('client_secret'),
    refresh_token=os.getenv('refresh_token'),
    redirect_uri=os.getenv('redirect_uri')
)

@app.route("/",method=["GET","POST"])
def home_page():
    #check if header has "type:form"
    #if it does, then it is a form submission
    if request.headers.get('type') == 'form':
        #get the form data
        form_data = request.form.to_dict()
        print(form_data)
        #insert the form data to the database
        result = mongo.db.task.insert_one(form_data)
        
        return f"{result}"
    elif request.headers.get('type') is None:
        #return the last 10 documents from the database according to timestamp
        return mongo.db.forms.find().sort([("timestamp", -1)]).limit(10)
    
    