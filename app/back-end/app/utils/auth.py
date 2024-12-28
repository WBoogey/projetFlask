##from flask import request, jsonify
##from functools import wraps
##from app.models.user_models import User
##
##def token_required(f):
##    @wraps(f)
##    def decorated(*args, **kwargs):
##        token = request.headers.get("Authorization")
##        if not token:
##            return jsonify({"error": "Token is missing!"}), 401
##        try:
##            user_id = User.verify_token(token)
##        except ValueError as e:
##            return jsonify({"error": str(e)}), 401
##        return f(user_id, *args, **kwargs)
##    return decorated
