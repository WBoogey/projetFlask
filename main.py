from flask import Flask, render_template
from app.models.scrutin_models import Scrutin
from dotenv import load_dotenv
load_dotenv()

from app import create_app

app = create_app()

@app.route('/')
def home():
    scrutins = Scrutin.get_all_scrutins()
    return render_template('home.html', scrutins=scrutins)

if __name__ == "__main__":
    try:
        print("Starting Flask application...")
        app.run(debug=True, host="0.0.0.0", port=5000)
    except Exception as e:
        print("Failed to start the application:", str(e))
