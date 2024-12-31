import unittest
from datetime import datetime, timedelta
from app import create_app, mongo
from mongomock import MongoClient
from app.models.vote_models import Vote

class TestVoteModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.testing = True

        # Mock MongoDB
        cls.mock_db = MongoClient().db  # Use mongomock as a mock database
        cls.app.config["MONGO_URI"] = None  # Disable actual MongoDB URI
        mongo.db = cls.mock_db  # Replace Flask-PyMongo's db with the mock DB

    def setUp(self):
        # Clean the mock scrutins and votes collections before each test
        self.mock_db.scrutins.delete_many({})
        self.mock_db.votes.delete_many({})

    def test_cast_vote(self):
        scrutin_id = self.mock_db.scrutins.insert_one({
            "title": "Election 2025",
            "description": "Presidential election",
            "options": ["Candidate A", "Candidate B"],
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow() + timedelta(days=1),  # Set end_date to the future
            "created_by": "admin_user",
            "is_active": True,
        }).inserted_id

        user_id = "test_user"
        preferences = {"Candidate A": 3, "Candidate B": 2}

        vote = Vote.cast_vote(user_id, scrutin_id, preferences)
        self.assertEqual(vote["preferences"], preferences)
        self.assertEqual(vote["user_id"], user_id)

    def test_modify_vote(self):
        scrutin_id = self.mock_db.scrutins.insert_one({
            "title": "Election 2025",
            "description": "Presidential election",
            "options": ["Candidate A", "Candidate B"],
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow() + timedelta(days=1),  # Set end_date to the future
            "created_by": "admin_user",
            "is_active": True,
        }).inserted_id

        user_id = "test_user"
        preferences = {"Candidate A": 3, "Candidate B": 2}

        # Cast an initial vote
        Vote.cast_vote(user_id, scrutin_id, preferences)

        # Modify the vote
        updated_preferences = {"Candidate A": 1, "Candidate B": 4}
        result = Vote.modify_vote(user_id, scrutin_id, updated_preferences)

        self.assertEqual(result["message"], "Vote mis à jour avec succès.")

    def test_get_votes(self):
        scrutin_id = self.mock_db.scrutins.insert_one({
            "title": "Election 2025",
            "description": "Presidential election",
            "options": ["Candidate A", "Candidate B"],
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow() + timedelta(days=1),
            "created_by": "admin_user",
            "is_active": True,
        }).inserted_id

        user_id = "test_user"
        preferences = {"Candidate A": 3, "Candidate B": 2}

        self.mock_db.votes.insert_one({
            "user_id": user_id,
            "scrutin_id": scrutin_id,
            "preferences": preferences,
            "cast_at": datetime.utcnow(),
        })

        votes = Vote.get_votes(scrutin_id)
        self.assertEqual(len(votes), 1)
        self.assertEqual(votes[0]["preferences"], preferences)
        self.assertEqual(votes[0]["user_id"], user_id)

if __name__ == "__main__":
    unittest.main()
