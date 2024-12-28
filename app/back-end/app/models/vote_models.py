from app import mongo
from bson.objectid import ObjectId
from datetime import datetime

class Vote:
    @staticmethod
    def cast_vote(user_id, scrutin_id, preferences):
        # Vérifier si l'utilisateur a déjà voté pour ce scrutin
        existing_vote = mongo.db.votes.find_one({"user_id": user_id, "scrutin_id": ObjectId(scrutin_id)})
        if existing_vote:
            raise ValueError("User has already voted for this scrutin.")

        # Vérifier si le scrutin est encore actif
        scrutin = mongo.db.scrutins.find_one({"_id": ObjectId(scrutin_id)})
        if not scrutin or not scrutin["is_active"] or scrutin["end_date"] < datetime.utcnow():
            raise ValueError("Scrutin is closed or does not exist.")

        # Enregistrer le vote
        vote = {
            "user_id": user_id,
            "scrutin_id": ObjectId(scrutin_id),
            "preferences": preferences,
            "cast_at": datetime.utcnow(),
        }
        result = mongo.db.votes.insert_one(vote)
        vote["_id"] = str(result.inserted_id)  # Convertir ObjectId en string pour JSON
        return vote

    @staticmethod
    def modify_vote(user_id, scrutin_id, preferences):
        # Vérifier si le scrutin est encore actif
        scrutin = mongo.db.scrutins.find_one({"_id": ObjectId(scrutin_id)})
        if not scrutin or not scrutin["is_active"] or scrutin["end_date"] < datetime.utcnow():
            raise ValueError("Scrutin is closed or does not exist.")

        # Mettre à jour le vote
        result = mongo.db.votes.update_one(
            {"user_id": user_id, "scrutin_id": ObjectId(scrutin_id)},
            {"$set": {"preferences": preferences, "updated_at": datetime.utcnow()}}
        )
        if result.matched_count == 0:
            raise ValueError("No vote found to update.")
        return {"message": "Vote updated successfully."}

    @staticmethod
    def get_votes(scrutin_id):
        votes = list(mongo.db.votes.find({"scrutin_id": ObjectId(scrutin_id)}))
        for vote in votes:
            vote["_id"] = str(vote["_id"])  # Convertir ObjectId en string
            vote["scrutin_id"] = str(vote["scrutin_id"])
        return votes
