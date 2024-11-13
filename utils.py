#instantiate the client
#this can then be used in views.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv('MONGO_URI')

client = MongoClient(uri)

db = client['data']
