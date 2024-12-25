from app import create_app

app = create_app()

if __name__ == "__main__":
    try:
        print("Starting Flask application...")
        app.run(debug=True, host="0.0.0.0", port=5000)
    except Exception as e:
        print("Failed to start the application:", str(e))
