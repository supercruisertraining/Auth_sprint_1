from functools import wraps

import jwt
from flask import request, jsonify

from core.config import config


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            return jsonify({"message": "Authorization failed. Token not found."}), 401
        try:
            data = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
            user_id = data.get("user_id")
            user_role = data.get("user_role", "")
            if not user_id:
                return jsonify({"message": "Invalid Authentication token."}), 401
        except Exception as e:
            return jsonify({"message": "Something went wrong"}), 500

        return f(user_id=user_id, user_role=user_role, *args, **kwargs)

    return decorated


def admin_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            return jsonify({"message": "Authorization failed. Token not found."}), 401
        try:
            data = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
            user_id = data.get("user_id")
            is_admin = data.get("is_admin", False)
            if not user_id or not is_admin:
                return jsonify({"message": "Invalid Authentication token."}), 401
        except Exception as e:
            return jsonify({"message": "Something went wrong"}), 500

        return f(user_id=user_id, *args, **kwargs)

    return decorated


def verify_oauth2_state(f):
    @wraps(f)
    def decorated(social_type: str):
        token = request.args.get("state")
        if not token:
            return jsonify({"message": "Wrong state."}), 401
        try:
            data = jwt.decode(token, config.JWT_OAUTH2_STATE_SECRET, algorithms=[config.JWT_ALGORITHM])
            social_type_from_state = data.get("type")
            is_oauth2_token = data.get("oauth2", False)
            if social_type_from_state != social_type or not is_oauth2_token:
                return jsonify({"message": "Invalid state token."}), 401
        except Exception as e:
            return jsonify({"message": "Something went wrong"}), 500

        return f(social_type)

    return decorated
