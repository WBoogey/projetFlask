from flask import Blueprint, request, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash
from ..models.user_models import User
from ..models.vote_models import Vote
from ..models.scrutin_models import Scrutin
from ..helper.convertion import ensure_datetime 

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Register a new user.
    """
    if request.method == 'POST':
        data = request.form
        required_fields = ["pseudonyme", "email", "date_naissance", "password"]
        for field in required_fields:
            if field not in data:
                return render_template("error.html", error=f"Champ manquant : {field}"), 400

        # Optional role field, default to 'user'
        role = data.get("role", "user")

        try:
            user = User.create_user(
                data["pseudonyme"], data["email"], data["date_naissance"], data["password"], role
            )
            return redirect(url_for('user_bp.login'))
        except ValueError as e:
            return render_template("error.html", error=str(e)), 400
        except Exception as e:
            return render_template("error.html", error=str(e)), 500
    return render_template("register.html")

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Authenticate and log in a user.
    """
    if request.method == 'POST':
        data = request.form
        required_fields = ["email", "password"]
        for field in required_fields:
            if field not in data:
                return render_template("error.html", error=f"Champ manquant : {field}"), 400

        try:
            user = User.authenticate_user(data["email"], data["password"])
            token = User.generate_token(user["_id"], user["role"])
            session['logged_in'] = True
            session['user_id'] = str(user["_id"])
            session['user_role'] = user["role"]
            if user["role"] == "admin":
                return redirect(url_for('user_bp.dashboard'))
            return redirect(url_for('user_bp.profile'))
        except ValueError as e:
            return render_template("error.html", error=str(e)), 401
        except Exception as e:
            return render_template("error.html", error=f"Erreur interne du serveur : {str(e)}"), 500
    return render_template("login.html")

@user_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@user_bp.route("/profile")
def profile():
    if not session.get("logged_in"):
        return redirect(url_for("user_bp.login"))
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("user_bp.login"))
    user = User.get_user_by_id(user_id)
    if not user:
        return render_template("error.html", error="Utilisateur non trouvé"), 404
    votes = User.get_user_votes(user_id)
    return render_template("profile.html", user=user, votes=votes)

@user_bp.route("/modify_vote/<vote_id>", methods=["GET", "POST"])
def modify_vote(vote_id):
    if not session.get("logged_in"):
        return redirect(url_for("user_bp.login"))
    if request.method == "POST":
        preferences = request.form.to_dict()
        Vote.modify_vote(session["user_id"], vote_id, preferences)
        return redirect(url_for("user_bp.profile"))
    vote = Vote.get_vote_by_id(vote_id)
    return render_template("modify_vote.html", vote=vote)

@user_bp.route("/results/<scrutin_id>")
def results(scrutin_id):
    if not session.get("logged_in"):
        return redirect(url_for("user_bp.login"))
    results = Scrutin.calculate_results(scrutin_id)
    return render_template("results.html", results=results)


@user_bp.route("/dashboard")
def dashboard():
    if not session.get("logged_in") or session.get("user_role") != "admin":
        return redirect(url_for("user_bp.login"))
    scrutins = Scrutin.get_all_scrutins()
    users = User.get_all_users()
    return render_template("admin_dashboard.html", scrutins=scrutins, users=users)

@user_bp.route("/create_scrutin", methods=["GET", "POST"])
def create_scrutin():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        options = request.form.getlist("options")
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        created_by = session["user_id"]
        Scrutin.create_scrutin(title, description, options, start_date, end_date, created_by)
        return redirect(url_for("admin_bp.dashboard"))
    return render_template("create_scrutin.html")

@user_bp.route("/modify_scrutin/<scrutin_id>", methods=["GET", "POST"])
def modify_scrutin(scrutin_id):
    if request.method == "POST":
        updates = request.form.to_dict()
        Scrutin.update_scrutin(scrutin_id, updates)
        return redirect(url_for("admin_bp.dashboard"))
    scrutin = Scrutin.get_scrutin_by_id(scrutin_id)
    return render_template("modify_scrutin.html", scrutin=scrutin)

@user_bp.route("/delete_scrutin/<scrutin_id>", methods=["POST"])
def delete_scrutin(scrutin_id):
    Scrutin.delete_scrutin(scrutin_id)
    return redirect(url_for("admin_bp.dashboard"))

@user_bp.route("/stop_scrutin/<scrutin_id>", methods=["POST"])
def stop_scrutin(scrutin_id):
    Scrutin.update_scrutin(scrutin_id, {"is_active": False})
    return redirect(url_for("admin_bp.dashboard"))

@user_bp.route("/delete_user/<user_id>", methods=["POST"])
def delete_user(user_id):
    User.delete_user(user_id)
    return redirect(url_for("admin_bp.dashboard"))
