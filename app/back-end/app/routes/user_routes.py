from flask import Blueprint, request, jsonify
from bson import ObjectId
from app.models.user_models import User

user_bp = Blueprint("users", __name__)

def serialize_user(user):
    """Serialize a MongoDB user document for JSON response."""
    user["_id"] = str(user["_id"])
    return user

@user_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    required_fields = ["pseudonyme", "email", "date_naissance", "password"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    try:
        user = User.create_user(
            data["pseudonyme"], data["email"], data["date_naissance"], data["password"]
        )
        user_serialized = serialize_user(user)
        return jsonify({"message": "User registered successfully", "user": user_serialized}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@user_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    required_fields = ["pseudonyme", "password"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    try:
        user = User.authenticate_user(data["pseudonyme"], data["password"])
        token = User.generate_token(user["_id"])
        return jsonify({"message": "Login successful", "token": token}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
