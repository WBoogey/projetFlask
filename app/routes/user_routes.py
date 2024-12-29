from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..models.user import User

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/')
def home():
    return render_template('home.html')

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        pseudonyme = request.form.get('pseudonyme')
        email = request.form.get('email')
        date_naissance = request.form.get('date_naissance')
        try:
            User.create_user(pseudonyme, email, date_naissance)
            flash('User registered successfully!', 'success')
            return redirect(url_for('user_bp.register'))
        except ValueError as e:
            flash(str(e), 'danger')
    return render_template('register.html')

@user_bp.route('/test', methods=['GET'])
def test_route():
    return "Test route is working!"