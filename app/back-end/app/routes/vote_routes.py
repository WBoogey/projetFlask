from flask import Blueprint, request, jsonify
from app.models.vote_models import Vote

vote_bp = Blueprint("votes", __name__)

@vote_bp.route("/<scrutin_id>", methods=["POST"])
def cast_vote(scrutin_id):
    """
    Route to cast a vote for a specific scrutin.
    """
    data = request.json
    required_fields = ["user_id", "preferences"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    try:
        vote = Vote.cast_vote(data["user_id"], scrutin_id, data["preferences"])
        return jsonify({"message": "Vote cast successfully", "vote": vote}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@vote_bp.route("/<scrutin_id>/votes", methods=["GET"])
def get_votes(scrutin_id):
    """
    Route to retrieve all votes for a specific scrutin.
    """
    try:
        votes = Vote.get_votes(scrutin_id)
        return jsonify({"votes": votes}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@vote_bp.route("/<scrutin_id>", methods=["PATCH"])
def modify_vote(scrutin_id):
    """
    Route to modify a vote for a specific scrutin.
    """
    data = request.json
    required_fields = ["user_id", "preferences"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    try:
        response = Vote.modify_vote(data["user_id"], scrutin_id, data["preferences"])
        return jsonify(response), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
