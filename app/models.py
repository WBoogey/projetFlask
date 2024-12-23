from flask_pymongo import MongoClient

def init_db(mongo):
    db = mongo.db
    return db
