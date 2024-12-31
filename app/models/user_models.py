from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import jwt
from datetime import datetime, timedelta
from app import mongo
from config import Config

class User:
    @staticmethod
    def create_user(pseudonyme, email, date_naissance, password, role="user"):
        """
        Create a new user in the database.
        """
        if not pseudonyme or not email or not date_naissance or not password:
            raise ValueError("All fields (pseudonyme, email, date_naissance, password) are required.")

        if mongo.db.users.find_one({"pseudonyme": pseudonyme}):
            raise ValueError("Pseudonyme already exists.")

        if role not in ["user", "admin"]:
            raise ValueError("Role must be 'user' or 'admin'.")

        hashed_password = generate_password_hash(password)
        user = {
            "pseudonyme": pseudonyme,
            "email": email,
            "date_naissance": date_naissance,
            "password": hashed_password,
            "etat": "actif",
            "role": role,  # Added role field
            "created_at": datetime.utcnow(),
        }
        result = mongo.db.users.insert_one(user)
        user["_id"] = str(result.inserted_id)  # Convert ObjectId to string
        return user

    @staticmethod
    def authenticate_user(email, password):
        """
        Authenticate a user by pseudonyme and password.
        """
        if not email or not password:
            raise ValueError("Pseudonyme and password are required.")

        user = mongo.db.users.find_one({"email": email})
        if not user or not check_password_hash(user["password"], password):
            raise ValueError("Invalid email or password.")

        user["_id"] = str(user["_id"])  # Convert ObjectId to string
        return user

    @staticmethod
    def generate_token(user_id, role):
        """
        Generate a JWT token for the user.
        """
        payload = {
            "user_id": str(user_id),
            "role": role,  # Include role in the token payload
            "exp": datetime.utcnow() + timedelta(hours=24),  # Token expires in 24 hours
        }
        return jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")

    @staticmethod
    def verify_token(token):
        """
        Verify a JWT token.
        """
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            return payload  # Return the full payload, including role
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired.")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token.")
        
    @staticmethod
    def get_all_users():
        users = list(mongo.db.users.find())
        for user in users:
            user["_id"] = str(user["_id"])  # Convert ObjectId to string
        return users
        
    @staticmethod
    def get_user_by_id(user_id):
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            user["_id"] = str(user["_id"])  # Convert ObjectId to string
        return user

    @staticmethod
    def get_user_by_email(email):
        user = mongo.db.users.find_one({"email": email})
        if user:
            user["_id"] = str(user["_id"])  # Convert ObjectId to string
        return user

    @staticmethod
    def update_user(user_id, updates):
        result = mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": updates})
        if result.matched_count == 0:
            raise ValueError("User not found.")
        return {"message": "User updated successfully."}

    @staticmethod
    def delete_user(user_id):
        result = mongo.db.users.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            raise ValueError("User not found.")
        return {"message": "User deleted successfully."}

    @staticmethod
    def get_user_votes(user_id):
        votes = list(mongo.db.votes.find({"user_id": user_id}))
        for vote in votes:
            vote["_id"] = str(vote["_id"])  # Convert ObjectId to string
            vote["scrutin_id"] = str(vote["scrutin_id"])
        return votes