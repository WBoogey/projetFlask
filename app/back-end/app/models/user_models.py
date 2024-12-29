from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from app import mongo
from app.config import Config

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
    def authenticate_user(pseudonyme, password):
        """
        Authenticate a user by pseudonyme and password.
        """
        if not pseudonyme or not password:
            raise ValueError("Pseudonyme and password are required.")

        user = mongo.db.users.find_one({"pseudonyme": pseudonyme})
        if not user or not check_password_hash(user["password"], password):
            raise ValueError("Invalid pseudonyme or password.")

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
