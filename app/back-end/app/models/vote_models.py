from app import mongo
from bson.objectid import ObjectId
from datetime import datetime


class Vote:
    @staticmethod
    def cast_vote(user_id, scrutin_id, preferences):
        """
        Cast a vote for a specific scrutin.
        """
        if not user_id or not scrutin_id:
            raise ValueError("User ID and Scrutin ID are required.")
        if not isinstance(preferences, dict):
            raise ValueError("Preferences must be a dictionary.")

        # Check if the user has already voted
        existing_vote = mongo.db.votes.find_one({"user_id": user_id, "scrutin_id": ObjectId(scrutin_id)})
        if existing_vote:
            raise ValueError("User has already voted for this scrutin.")

        # Check if the scrutin is still active
        scrutin = mongo.db.scrutins.find_one({"_id": ObjectId(scrutin_id)})
        if not scrutin:
            raise ValueError("Scrutin does not exist.")
        if not scrutin["is_active"] or scrutin["end_date"] < datetime.utcnow():
            raise ValueError("Scrutin is closed or inactive.")

        # Validate preferences match scrutin options
        if not all(option in scrutin["options"] for option in preferences.keys()):
            raise ValueError("Invalid preferences. Options must match scrutin's available choices.")

        # Save the vote
        vote = {
            "user_id": user_id,
            "scrutin_id": ObjectId(scrutin_id),
            "preferences": preferences,
            "cast_at": datetime.utcnow(),
        }
        result = mongo.db.votes.insert_one(vote)
        vote["_id"] = str(result.inserted_id)  # Convert ObjectId to string for JSON serialization
        vote["scrutin_id"] = str(vote["scrutin_id"])
        return vote

    @staticmethod
    def modify_vote(user_id, scrutin_id, preferences):
        """
        Modify an existing vote for a specific scrutin.
        """
        if not user_id or not scrutin_id:
            raise ValueError("User ID and Scrutin ID are required.")
        if not isinstance(preferences, dict):
            raise ValueError("Preferences must be a dictionary.")

        # Check if the scrutin is still active
        scrutin = mongo.db.scrutins.find_one({"_id": ObjectId(scrutin_id)})
        if not scrutin:
            raise ValueError("Scrutin does not exist.")
        if not scrutin["is_active"] or scrutin["end_date"] < datetime.utcnow():
            raise ValueError("Scrutin is closed or inactive.")

        # Validate preferences match scrutin options
        if not all(option in scrutin["options"] for option in preferences.keys()):
            raise ValueError("Invalid preferences. Options must match scrutin's available choices.")

        # Update the vote
        result = mongo.db.votes.update_one(
            {"user_id": user_id, "scrutin_id": ObjectId(scrutin_id)},
            {"$set": {"preferences": preferences, "updated_at": datetime.utcnow()}}
        )
        if result.matched_count == 0:
            raise ValueError("No vote found to update.")
        return {"message": "Vote updated successfully."}

    @staticmethod
    def get_votes(scrutin_id):
        """
        Get all votes for a specific scrutin.
        """
        if not scrutin_id:
            raise ValueError("Scrutin ID is required.")
        votes = list(mongo.db.votes.find({"scrutin_id": ObjectId(scrutin_id)}))
        for vote in votes:
            vote["_id"] = str(vote["_id"])  # Convert ObjectId to string
            vote["scrutin_id"] = str(vote["scrutin_id"])
        return votes
