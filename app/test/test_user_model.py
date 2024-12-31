import unittest
from app import create_app, mongo
from mongomock import MongoClient
from app.models.user_models import User
from werkzeug.security import check_password_hash


class TestUserModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.testing = True

        # Mock MongoDB
        cls.mock_db = MongoClient().db  # Use mongomock as a mock database
        cls.app.config["MONGO_URI"] = None  # Disable actual MongoDB URI
        mongo.db = cls.mock_db  # Replace Flask-PyMongo's db with the mock DB

    def setUp(self):
        # Clean the mock users collection before each test
        self.mock_db.users.delete_many({})

    def test_create_user(self):
        pseudonyme = "test_user"
        email = "test@example.com"
        date_naissance = "2000-01-01"
        password = "password123"
        role = "user"

        user = User.create_user(pseudonyme, email, date_naissance, password, role)
        self.assertEqual(user["pseudonyme"], pseudonyme)
        self.assertTrue(check_password_hash(user["password"], password))
        self.assertEqual(user["role"], role)

    def test_authenticate_user(self):
        email = "test@example.com"
        password = "password123"

        # Create a user in the mock database
        User.create_user("test_user", email, "2000-01-01", password)

        # Authenticate the user
        user = User.authenticate_user(email, password)
        self.assertEqual(user["email"], email)

    def test_generate_token(self):
        user = User.create_user("test_user", "test@example.com", "2000-01-01", "password123", "admin")
        token = User.generate_token(user["_id"], user["role"])

        # Decode the token and check the payload
        decoded_payload = User.verify_token(token)
        self.assertEqual(decoded_payload["user_id"], user["_id"])
        self.assertEqual(decoded_payload["role"], user["role"])
