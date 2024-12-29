from flask import Blueprint, request, jsonify
from bson import ObjectId
from app.models.scrutin_models import Scrutin
from datetime import datetime
from app.utils.auth import verify_token_and_role

scrutin_bp = Blueprint("scrutins", __name__)

@scrutin_bp.route("/create", methods=["POST"])
def create_scrutin():
    """
    Create a new scrutin (Admin-only).
    """
    auth_response = verify_token_and_role(required_role="admin")
    if isinstance(auth_response, tuple):  # Unauthorized response
        return auth_response

    data = request.json
    required_fields = ["title", "options", "start_date", "end_date", "created_by"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    try:
        scrutin = Scrutin.create_scrutin(
            data["title"],
            data.get("description", ""),
            data["options"],
            data["start_date"],
            data["end_date"],
            data["created_by"],
        )
        return jsonify({"message": "Scrutin created successfully", "scrutin": scrutin}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@scrutin_bp.route("/", methods=["GET"])
def get_scrutins():
    scrutins = Scrutin.get_all_scrutins()
    return jsonify(scrutins), 200

@scrutin_bp.route("/<scrutin_id>", methods=["GET"])
def get_scrutin(scrutin_id):
    try:
        scrutin = Scrutin.get_scrutin(scrutin_id)
        if not scrutin:
            return jsonify({"error": "Scrutin not found"}), 404
        return jsonify(scrutin), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@scrutin_bp.route("/<scrutin_id>", methods=["PATCH"])
def update_scrutin(scrutin_id):
    updates = request.json
    try:
        Scrutin.update_scrutin(scrutin_id, updates)
        return jsonify({"message": "Scrutin updated successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@scrutin_bp.route("/<scrutin_id>", methods=["DELETE"])
def delete_scrutin(scrutin_id):
    """
    Delete a scrutin (Admin-only).
    """
    auth_response = verify_token_and_role(required_role="admin")
    if isinstance(auth_response, tuple):  # Unauthorized response
        return auth_response
    try:
        Scrutin.delete_scrutin(scrutin_id)
        return jsonify({"message": "Scrutin deleted successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@scrutin_bp.route("/<scrutin_id>/results", methods=["GET"])
def get_results(scrutin_id):
    try:
        scrutin = Scrutin.get_scrutin(scrutin_id)
        if not scrutin:
            return jsonify({"error": "Scrutin not found"}), 404
        if datetime.utcnow() < scrutin["end_date"]:
            return jsonify({"error": "Results are not available until the scrutin ends"}), 403
        results = Scrutin.calculate_results(scrutin_id)
        return jsonify({"results": results}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@scrutin_bp.route("/<scrutin_id>/stats", methods=["GET"])
def get_statistics(scrutin_id):
    try:
        scrutin = Scrutin.get_scrutin(scrutin_id)
        if not scrutin:
            return jsonify({"error": "Scrutin not found"}), 404
        stats = Scrutin.get_statistics(scrutin_id)
        return jsonify({"statistics": stats}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@scrutin_bp.route("/platform-stats", methods=["GET"])
def get_platform_statistics():
    try:
        stats = Scrutin.get_platform_statistics()
        return jsonify({"platform_statistics": stats}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@scrutin_bp.route("/<scrutin_id>/disable", methods=["PATCH"])
def disable_scrutin(scrutin_id):
    try:
        Scrutin.update_scrutin(scrutin_id, {"is_active": False})
        return jsonify({"message": "Scrutin disabled successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400
