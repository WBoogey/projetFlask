from app import mongo

class User:
    @staticmethod
    def create_user(pseudonyme, email, date_naissance):
        """Create a new user in the database."""
        if mongo.db.users.find_one({"pseudonyme": pseudonyme}):
            raise ValueError("Pseudonyme already exists.")
        user = {
            "pseudonyme": pseudonyme,
            "email": email,
            "date_naissance": date_naissance,
            "etat": "actif"
        }
        result = mongo.db.users.insert_one(user)
        user["_id"] = result.inserted_id  # Add the ObjectId to the user dictionary
        return user
