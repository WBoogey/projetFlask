from flask import Flask
from flask_pymongo import PyMongo
from flask_cors import CORS
from app.config import Config

# MongoDB client
mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for cross-origin requests

    # Load configuration
    app.config.from_object(Config)

    # Initialize extensions
    mongo.init_app(app)

    # Test MongoDB connection during app creation
    try:
        collections = mongo.db.list_collection_names()
        print("MongoDB connection successful!")
        print(f"Collections in the database: {collections}")
    except Exception as e:
        print("MongoDB connection failed:", str(e))

    # Register blueprints
    from app.routes.user_routes import user_bp
    app.register_blueprint(user_bp, url_prefix="/users")

    return app
