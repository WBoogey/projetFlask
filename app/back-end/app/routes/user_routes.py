from flask import Blueprint, request, jsonify
from bson import ObjectId
from app.models.user import User

user_bp = Blueprint("users", __name__)

def serialize_user(user):
    """Serialize a MongoDB user document for JSON response."""
    user["_id"] = str(user["_id"])
    return user

@user_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    try:
        user = User.create_user(data["pseudonyme"], data["email"], data["date_naissance"])
        user_serialized = serialize_user(user)  # Serialize the user object
        return jsonify({"message": "User registered successfully", "user": user_serialized}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
