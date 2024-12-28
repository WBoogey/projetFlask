from flask import Blueprint, request, jsonify
from app.models.vote_models import Vote

vote_bp = Blueprint("votes", __name__)

@vote_bp.route("/<scrutin_id>", methods=["POST"])
def cast_vote(scrutin_id):
    data = request.json
    try:
        vote = Vote.cast_vote(data["user_id"], scrutin_id, data["preferences"])
        return jsonify({"message": "Vote cast successfully", "vote": vote}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@vote_bp.route("/<scrutin_id>/votes", methods=["GET"])
def get_votes(scrutin_id):
    try:
        votes = Vote.get_votes(scrutin_id)
        return jsonify({"votes": votes}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@vote_bp.route("/<scrutin_id>", methods=["PATCH"])
def modify_vote(scrutin_id):
    data = request.json
    try:
        response = Vote.modify_vote(data["user_id"], scrutin_id, data["preferences"])
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
