from flask import request, jsonify
import jwt
from bson.objectid import ObjectId
from app import mongo
from app.config import Config

def verify_token_and_role(required_role=None):
    """
    Verify JWT token and user role.
    """
    # Extract the token from the Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Token is missing or invalid format."}), 401

    token = auth_header.split(" ")[1]

    try:
        # Decode token
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if not user_id:
            return jsonify({"error": "Token payload is invalid."}), 401

        # Fetch user from the database
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"error": "User not found."}), 404

        # Check for required role
        if required_role and user.get("role") != required_role:
            return jsonify({"error": "Unauthorized: Insufficient permissions."}), 403

        return user
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token."}), 401

