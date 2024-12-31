from flask import Blueprint, request, render_template, redirect, url_for, session
from ..utils.auth import verify_token_and_role
from ..models.scrutin_models import Scrutin

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
    required_fields = ["title", "description", "options", "start_date", "end_date", "created_by"]
    for field in required_fields:
        if field not in data:
            return render_template("error.html", error=f"Missing field: {field}"), 400

    try:
        scrutin = Scrutin.create_scrutin(
            title=data["title"],
            description=data["description"],
            options=data["options"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            created_by=data["created_by"]
        )
        return render_template("scrutin_created.html", scrutin=scrutin), 201
    except ValueError as e:
        return render_template("error.html", error=str(e)), 400
    except Exception as e:
        return render_template("error.html", error=str(e)), 500
    
@scrutin_bp.route("/details/<scrutin_id>", methods=["GET"])
def scrutin_details(scrutin_id):
    """
    Show details of a specific scrutin.
    """
    if not session.get('logged_in'):
        return redirect(url_for('user_bp.register'))
    
    scrutin = Scrutin.get_scrutin_by_id(scrutin_id)
    if not scrutin:
        return render_template("error.html", error="Scrutin not found"), 404
    return render_template("scrutin_details.html", scrutin=scrutin)

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
        return render_template("scrutin_deleted.html", message="Scrutin deleted successfully"), 200
    except ValueError as e:
        return render_template("error.html", error=str(e)), 404
    except Exception as e:
        return render_template("error.html", error=str(e)), 400

@scrutin_bp.route("/<scrutin_id>/results", methods=["GET"])
def get_results(scrutin_id):
    try:
        results = Scrutin.get_results(scrutin_id)
        return render_template("results.html", results=results), 200
    except ValueError as e:
        return render_template("error.html", error=str(e)), 404
    except Exception as e:
        return render_template("error.html", error=str(e)), 400