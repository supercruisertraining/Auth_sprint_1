from flask import request, jsonify, Blueprint

from schemas.user import UserRegisterModel, UserUpdateModel
from services.user_service import get_user_service
from utils.auth import token_required

users_blueprint_v1 = Blueprint("users_blueprint_v1", __name__, url_prefix="/api/v1")


@users_blueprint_v1.route("/create_user", methods=["POST"])
def create_user():
    """
    Создать пользователя
    ---
    parameters:
      - name: body
        in: body
        schema:
          properties:
            username:
              type: string
            password:
              type: string
    responses:
        200:
            description: Success
    """
    new_user = UserRegisterModel(**request.json)
    user_service = get_user_service()
    is_valid, reason = user_service.validate_to_create(new_user)
    if not is_valid:
        return jsonify({"message": reason}), 409
    new_id = user_service.create_user(new_user)

    return jsonify({"user_id": new_id}), 200


@users_blueprint_v1.route("/update_user", methods=["PATCH"])
@token_required
def update_user(user_id: str, *args, **kwargs):
    """
    Изменить данные пользователя
    ---
    security:
      - APIKeyHeader: ['Authorization']
    parameters:
      - name: body
        in: body
        schema:
          properties:
            username:
              type: string
            password:
              type: string
            first_name:
              type: string
            last_name:
              type: string
    responses:
        200:
            description: Success
    """
    user = UserUpdateModel(**request.json)
    user_service = get_user_service()
    exist_user = user_service.get_user_by_user_id(user_id)
    if user.username and exist_user.username == user.username:
        user.username = None
    is_valid, reason = user_service.validate_to_create(user)
    if not is_valid:
        return jsonify({"message": reason}), 409
    user_service.update_user(user_id, user)

    return jsonify({"user_id": user_id}), 200


@users_blueprint_v1.route("/get_login_stat", methods=["GET"])
@token_required
def get_login_stat_list(user_id: str, *args, **kwargs):
    """
    Получить историю входов в аккаунт
    ---
    security:
      - APIKeyHeader: ['Authorization']
    responses:
        200:
            description: Success
    """
    user_service = get_user_service()
    login_stat = user_service.get_login_stat_list(user_id)
    return jsonify(login_stat), 200
