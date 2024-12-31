from faker import Faker
from werkzeug.security import generate_password_hash
from app import create_app, mongo
from config import Config
from dotenv import load_dotenv
load_dotenv()

fake = Faker()

def populate_users_table(num_users=10):
    app = create_app()
    with app.app_context():
        # Create an admin user
        admin_user = {
            "pseudonyme": "admin",
            "email": "admin@example.com",
            "date_naissance": "1980-01-01",
            "password": generate_password_hash("admin123"),
            "etat": "actif",
            "role": "admin",
            "created_at": fake.date_time_this_year(),
        }
        if not mongo.db.users.find_one({"pseudonyme": "admin"}):
            mongo.db.users.insert_one(admin_user)
            print("Admin user created.")

        # Generate random users
        for _ in range(num_users):
            pseudonyme = fake.unique.user_name()
            email = fake.unique.email()
            date_naissance = fake.date_of_birth(minimum_age=18, maximum_age=65).isoformat()
            password = generate_password_hash("password123")
            role = "user"

            # Ensure pseudonyme uniqueness
            while mongo.db.users.find_one({"pseudonyme": pseudonyme}):
                pseudonyme = fake.unique.user_name()

            user = {
                "pseudonyme": pseudonyme,
                "email": email,
                "date_naissance": date_naissance,
                "password": password,
                "etat": "actif",
                "role": role,
                "created_at": fake.date_time_this_year(),
            }

            mongo.db.users.insert_one(user)

        print(f"Populated the database with {num_users} users.")

if __name__ == "__main__":
    populate_users_table(num_users=10)