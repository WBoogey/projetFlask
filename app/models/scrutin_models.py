from app import mongo
from bson.objectid import ObjectId
from datetime import datetime
from ..helper.convertion import ensure_datetime

class Scrutin:
    @staticmethod
    def create_scrutin(title, description, options, start_date, end_date, created_by):
        if len(options) < 2:
            raise ValueError("A scrutin must have at least two options.")

        start_date = Scrutin.ensure_datetime(start_date)
        end_date = Scrutin.ensure_datetime(end_date)

        scrutin = {
            "title": title,
            "description": description,
            "options": options,
            "start_date": start_date,
            "end_date": end_date,
            "created_by": created_by,
            "created_at": datetime.utcnow(),
            "is_active": True,
        }

        result = mongo.db.scrutins.insert_one(scrutin)
        scrutin["_id"] = str(result.inserted_id)  # Convert ObjectId to string for JSON serialization
        return scrutin

    @staticmethod
    def get_all_scrutins():
        scrutins = list(mongo.db.scrutins.find())
        for scrutin in scrutins:
            scrutin["_id"] = str(scrutin["_id"])  # Serialize ObjectId
        return scrutins
    
    @staticmethod
    def get_scrutin_by_id(scrutin_id):
        scrutin = mongo.db.scrutins.find_one({"_id": ObjectId(scrutin_id)})
        if scrutin:
            scrutin["_id"] = str(scrutin["_id"])  # Convert ObjectId to string
        return scrutin

    @staticmethod
    def get_scrutin(scrutin_id):
        scrutin = mongo.db.scrutins.find_one({"_id": ObjectId(scrutin_id)})
        if scrutin:
            scrutin["_id"] = str(scrutin["_id"])  # Serialize ObjectId
        return scrutin

    @staticmethod
    def update_scrutin(scrutin_id, updates):
        result = mongo.db.scrutins.update_one({"_id": ObjectId(scrutin_id)}, {"$set": updates})
        if result.matched_count == 0:
            raise ValueError("Scrutin not found.")

    @staticmethod
    def delete_scrutin(scrutin_id):
        result = mongo.db.scrutins.delete_one({"_id": ObjectId(scrutin_id)})
        if result.deleted_count == 0:
            raise ValueError("Scrutin not found.")

    @staticmethod
    def calculate_results(scrutin_id):
        votes = mongo.db.votes.find({"scrutin_id": ObjectId(scrutin_id)})
        results = {}
        for vote in votes:
            for option, weight in vote["preferences"].items():
                if option not in results:
                    results[option] = 0
                results[option] += weight
        sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
        return sorted_results

    @staticmethod
    def get_statistics(scrutin_id):
        votes = list(mongo.db.votes.find({"scrutin_id": ObjectId(scrutin_id)}))
        stats = {
            "total_votes": len(votes),
            "vote_distribution": {}
        }
        for vote in votes:
            for option, weight in vote["preferences"].items():
                if option not in stats["vote_distribution"]:
                    stats["vote_distribution"][option] = 0
                stats["vote_distribution"][option] += weight
        return stats

    @staticmethod
    def get_platform_statistics():
        scrutins = list(mongo.db.scrutins.find())
        total_scrutins = len(scrutins)
        total_votes = mongo.db.votes.count_documents({})
        avg_options = sum(len(scrutin["options"]) for scrutin in scrutins) / total_scrutins if total_scrutins else 0
        return {
            "total_scrutins": total_scrutins,
            "total_votes": total_votes,
            "avg_options_per_scrutin": avg_options
        }