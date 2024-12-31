from flask import Blueprint, request, render_template, session
from ..models.vote_models import Vote
from ..models.scrutin_models import Scrutin

vote_bp = Blueprint("votes", __name__)

@vote_bp.route("/<scrutin_id>", methods=["POST"])
def cast_vote(scrutin_id):
    """
    Route pour enregistrer un vote pour un scrutin spécifique.
    """
    user_id = session.get('logged_in')
    if not user_id:
        return render_template("error.html", error="Utilisateur non connecté"), 401

    data = request.form
    preferences = {}

    for key, value in data.items():
        if key.startswith("preferences[") and key.endswith("]"):
            option = key[12:-1]  # Extraire le nom de l'option
            try:
                preference = int(value)
                if preference > 0:
                    preferences[option] = preference
            except ValueError:
                continue  # Ignorer les valeurs non numériques

    if not preferences:
        return render_template("error.html", error="Aucune préférence valide n'a été soumise"), 400

    try:
        # Trier les préférences par valeur
        sorted_preferences = dict(sorted(preferences.items(), key=lambda item: item[1]))
        
        vote = Vote.cast_vote(user_id, scrutin_id, sorted_preferences)
        return render_template("vote_cast.html", vote=vote), 201
    except ValueError as e:
        return render_template("error.html", error=str(e)), 400
    except Exception as e:
        return render_template("error.html", error=f"Erreur interne du serveur : {str(e)}"), 500

@vote_bp.route("/<scrutin_id>/votes", methods=["GET"])
def get_votes(scrutin_id):
    """
    Route to get all votes for a specific scrutin.
    """
    try:
        votes = Vote.get_votes(scrutin_id)
        return render_template("votes.html", votes=votes), 200
    except ValueError as e:
        return render_template("error.html", error=str(e)), 400
    except Exception as e:
        return render_template("error.html", error=f"Internal server error: {str(e)}"), 500

@vote_bp.route("/<scrutin_id>", methods=["PATCH"])
def modify_vote(scrutin_id):
    """
    Route to modify a vote for a specific scrutin.
    """
    data = request.form
    required_fields = ["user_id", "preferences"]
    for field in required_fields:
        if field not in data:
            return render_template("error.html", error=f"Missing field: {field}"), 400

    try:
        preferences = {key: int(value) for key, value in data.items() if key.startswith("preferences[")}
        # Exclure les valeurs négatives
        preferences = {key: value for key, value in preferences.items() if value > 0}
        # Trier les préférences par valeur
        sorted_preferences = dict(sorted(preferences.items(), key=lambda item: item[1]))
        response = Vote.modify_vote(data["user_id"], scrutin_id, sorted_preferences)
        return render_template("vote_modified.html", response=response), 200
    except ValueError as e:
        return render_template("error.html", error=str(e)), 400
    except Exception as e:
        return render_template("error.html", error=f"Internal server error: {str(e)}"), 500
    
@vote_bp.route("/<scrutin_id>/vote", methods=["GET"])
def vote(scrutin_id):
    """
    Show the voting page for a specific scrutin.
    """
    scrutin = Scrutin.get_scrutin_by_id(scrutin_id)
    if not scrutin:
        return render_template("error.html", error="Scrutin not found"), 404
    return render_template("votes.html", scrutin=scrutin)