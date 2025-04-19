import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from utils import load_config

def get_mongo_connection():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    config = load_config()
    p = config["MONGODB_P"]

    uri = f"mongodb+srv://huyangaloha:{p}@cluster0.vb0c5.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client["social_media"]

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        # print("Pinged your deployment. You successfully connected to MongoDB!")
        # print(f"Database: {db.name}, Collections: {db.list_collection_names()}")
    except Exception as e:
        print(e)

    return db

# get_mongo_connection()