from app import create_app  # Assurez-vous que le chemin vers 'create_app' est correct

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
