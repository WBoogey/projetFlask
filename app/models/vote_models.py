from app import mongo
from bson.objectid import ObjectId
from datetime import datetime
from .scrutin_models import Scrutin


class Vote:
    @staticmethod
    def cast_vote(user_id, scrutin_id, preferences):
        """
        Enregistrer un vote pour un scrutin spécifique.
        """
        if not user_id:
            raise ValueError("L'ID de l'utilisateur est requis.")
        
        if not preferences:
            raise ValueError("Les préférences sont requises.")

        scrutin = mongo.db.scrutins.find_one({"_id": ObjectId(scrutin_id)})
        if not scrutin:
            raise ValueError("Le scrutin n'existe pas.")
        
        # Utiliser la méthode ensure_datetime de Scrutin
        end_date = Scrutin.ensure_datetime(scrutin["end_date"])
        
        if not scrutin["is_active"] or end_date < datetime.utcnow():
            raise ValueError("Le scrutin est fermé ou inactif.")

        # Valider que les préférences correspondent aux options du scrutin
        if not all(option in scrutin["options"] for option in preferences.keys()):
            raise ValueError("Préférences invalides. Les options doivent correspondre aux choix disponibles du scrutin.")

        # Enregistrer le vote
        vote = {
            "user_id": user_id,
            "scrutin_id": ObjectId(scrutin_id),
            "preferences": preferences,
            "cast_at": datetime.utcnow(),
        }
        result = mongo.db.votes.insert_one(vote)
        vote["_id"] = str(result.inserted_id)  # Convertir ObjectId en chaîne pour la sérialisation JSON
        vote["scrutin_id"] = str(vote["scrutin_id"])
        return vote

    @staticmethod
    def modify_vote(user_id, scrutin_id, preferences):
        """
        Modifier un vote existant pour un scrutin spécifique.
        """
        if not user_id or not scrutin_id:
            raise ValueError("L'ID de l'utilisateur et l'ID du scrutin sont requis.")
        if not isinstance(preferences, dict):
            raise ValueError("Les préférences doivent être un dictionnaire.")

        scrutin = mongo.db.scrutins.find_one({"_id": ObjectId(scrutin_id)})
        if not scrutin:
            raise ValueError("Le scrutin n'existe pas.")
        
        # Convertir les dates de début et de fin en objets datetime
        end_date = Scrutin.ensure_datetime(scrutin["end_date"])
        
        if not scrutin["is_active"] or end_date < datetime.utcnow():
            raise ValueError("Le scrutin est fermé ou inactif.")

        # Valider que les préférences correspondent aux options du scrutin
        if not all(option in scrutin["options"] for option in preferences.keys()):
            raise ValueError("Préférences invalides. Les options doivent correspondre aux choix disponibles du scrutin.")

        # Mettre à jour le vote
        result = mongo.db.votes.update_one(
            {"user_id": user_id, "scrutin_id": ObjectId(scrutin_id)},
            {"$set": {"preferences": preferences, "modified_at": datetime.utcnow()}}
        )
        if result.matched_count == 0:
            raise ValueError("Le vote n'a pas été trouvé.")
        return {"message": "Vote mis à jour avec succès."}

    @staticmethod
    def get_votes(scrutin_id):
        """
        Obtenir tous les votes pour un scrutin spécifique.
        """
        if not scrutin_id:
            raise ValueError("L'ID du scrutin est requis.")
        votes = list(mongo.db.votes.find({"scrutin_id": ObjectId(scrutin_id)}))
        for vote in votes:
            vote["_id"] = str(vote["_id"])  # Convertir ObjectId en chaîne
            vote["scrutin_id"] = str(vote["scrutin_id"])
        return votes