from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import mongo

main = Blueprint('main', __name__)

@main.route("/")
def home():
    return render_template("home.html")

@main.route("/scrutins")
def scrutins():
    # Récupérer les scrutins de la base
    scrutins = mongo.db.scrutins.find()
    return render_template("scrutins.html", scrutins=scrutins)
