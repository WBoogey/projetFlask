import unittest
from app import create_app, mongo
from mongomock import MongoClient
from app.models.scrutin_models import Scrutin
from datetime import datetime


class TestScrutinModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.testing = True
        cls.client = cls.app.test_client()  # Flask test client for making requests

        # Mock MongoDB
        cls.mock_db = MongoClient().db  # Use mongomock as a mock database
        cls.app.config["MONGO_URI"] = None  # Disable actual MongoDB URI
        mongo.db = cls.mock_db  # Replace Flask-PyMongo's db with the mock DB

    def setUp(self):
        # Clean the mock scrutins collection before each test
        self.mock_db.scrutins.delete_many({})
        self.mock_db.votes.delete_many({})

    def test_create_scrutin(self):
        title = "Election 2025"
        description = "Presidential election"
        options = ["Candidate A", "Candidate B"]
        start_date = "2025-01-01"
        end_date = "2025-01-15"
        created_by = "admin_user"

        scrutin = Scrutin.create_scrutin(
            title, description, options, start_date, end_date, created_by
        )
        self.assertEqual(scrutin["title"], title)
        self.assertTrue(scrutin["is_active"])

    def test_get_all_scrutins(self):
        # Add a sample scrutin to the mock database
        self.mock_db.scrutins.insert_one({
            "title": "Sample Election",
            "description": "Sample description",
            "options": ["Option A", "Option B"],
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow(),
            "created_by": "admin_user",
            "is_active": True,
        })

        scrutins = Scrutin.get_all_scrutins()
        self.assertEqual(len(scrutins), 1)

    def test_calculate_results(self):
        # Insert sample votes and calculate results
        scrutin_id = self.mock_db.scrutins.insert_one({
            "title": "Election 2025",
            "description": "Presidential election",
            "options": ["Candidate A", "Candidate B"],
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow(),
            "created_by": "admin_user",
            "is_active": True,
        }).inserted_id

        self.mock_db.votes.insert_many([
            {"scrutin_id": scrutin_id, "preferences": {"Candidate A": 3, "Candidate B": 2}},
            {"scrutin_id": scrutin_id, "preferences": {"Candidate A": 1, "Candidate B": 2}},
        ])

        results = Scrutin.calculate_results(str(scrutin_id))
        self.assertEqual(results[0][0], "Candidate A")
        self.assertEqual(results[0][1], 4)  # Total votes for Candidate A
        self.assertEqual(results[1][0], "Candidate B")
        self.assertEqual(results[1][1], 4)  # Total votes for Candidate B
