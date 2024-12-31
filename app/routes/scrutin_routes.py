from flask import Blueprint, request, render_template, redirect, url_for, session
from ..utils.auth import verify_token_and_role
from ..models.scrutin_models import Scrutin
from ..models.vote_models import Vote
from ..helper.convertion import ensure_datetime

scrutin_bp = Blueprint("scrutins", __name__)

@scrutin_bp.route('/create_scrutin', methods=['GET', 'POST'])
def create_scrutin():
    """
    Create a new scrutin.
    """
    auth_response = verify_token_and_role(required_role="admin")
    if isinstance(auth_response, tuple):  # Unauthorized response
        return auth_response
    
    if request.method == 'POST':
        data = request.form
        required_fields = ["title", "description", "options", "start_date", "end_date"]
        for field in required_fields:
            if field not in data:
                return render_template("error.html", error=f"Champ manquant : {field}"), 400

        try:
            options = [option.strip() for option in data["options"].split(';')]
            scrutin = Scrutin.create_scrutin(
                title=data["title"],
                description=data["description"],
                options=options,
                start_date=ensure_datetime(data["start_date"]),
                end_date=ensure_datetime(data["end_date"]),
                created_by=session['user_id']
            )
            return redirect(url_for('user_bp.dashboard'))
        except ValueError as e:
            return render_template("error.html", error=str(e)), 400
        except Exception as e:
            return render_template("error.html", error=str(e)), 500
    return render_template("create_scrutin.html")
    
@scrutin_bp.route("/all", methods=["GET"])
def get_all_scrutins():
    """
    Get all scrutins.
    """
    scrutins = Scrutin.get_all_scrutins()
    return render_template("all_scrutins.html", scrutins=scrutins)
    
@scrutin_bp.route("/details/<scrutin_id>", methods=["GET"])
def scrutin_details(scrutin_id):
    """
    Get details of a specific scrutin.
    """
    scrutin = Scrutin.get_scrutin_by_id(scrutin_id)
    if not scrutin:
        return render_template("error.html", error="Scrutin not found"), 404

    votes = Vote.get_votes_by_scrutin(scrutin_id)
    num_votes = len(votes)
    is_active = scrutin["is_active"]

    return render_template("scrutin_details.html", scrutin=scrutin, num_votes=num_votes, is_active=is_active)

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
        return  redirect(url_for("user_bp.dashboard"))
    except ValueError as e:
        return render_template("error.html", error=str(e)), 404
    except Exception as e:
        return render_template("error.html", error=str(e)), 400

@scrutin_bp.route("/<scrutin_id>/results", methods=["GET"])
def get_results(scrutin_id):
    try:
        results = Scrutin.get_results(scrutin_id)
        return redirect(url_for("user_bp.dashboard")), 200
    except ValueError as e:
        return render_template("error.html", error=str(e)), 404
    except Exception as e:
        return render_template("error.html", error=str(e)), 400