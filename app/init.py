from flask import Flask
from flask_pymongo import PyMongo

mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    app.config["MONGO_URI"] = "mongodb://localhost:27017/scrutin_app"
    app.config["SECRET_KEY"] = "your_secret_key_here"
    mongo.init_app(app)
    return app