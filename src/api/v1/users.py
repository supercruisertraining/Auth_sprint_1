from http import HTTPStatus

from flask import request, jsonify, Blueprint

from schemas.user import UserRegisterModel, UserUpdateModel
from services.user_service import get_user_service
from utils.auth import token_required
from log.logger import custom_logger

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
    custom_logger.info(f"Trying to register user {new_user.username}")
    user_service = get_user_service()
    is_valid, reason = user_service.validate_to_create(new_user)
    if not is_valid:
        custom_logger.info(f"Username {new_user.username} is not valid")
        return jsonify({"message": reason}), HTTPStatus.CONFLICT
    new_id = user_service.create_user(new_user)

    return jsonify({"user_id": new_id}), HTTPStatus.OK


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
    custom_logger.info(f"Trying to update user {user.username}")
    user_service = get_user_service()
    exist_user = user_service.get_user_by_user_id(user_id)
    if user.username and exist_user.username == user.username:
        user.username = None
    is_valid, reason = user_service.validate_to_create(user)
    if not is_valid:
        custom_logger.info(f"Updating not valid for user {user.username}")
        return jsonify({"message": reason}), HTTPStatus.CONFLICT
    user_service.update_user(user_id, user)

    return jsonify({"user_id": user_id}), HTTPStatus.OK


@users_blueprint_v1.route("/get_login_stat", methods=["GET"])
@token_required
def get_login_stat_list(user_id: str, *args, **kwargs):
    """
    Получить историю входов в аккаунт
    ---
    security:
      - APIKeyHeader: ['Authorization']
    parameters:
      - name: page_size
        in: query
        type: integer
        example: 50
      - name: page_number
        in: query
        type: integer
        example: 1
    responses:
        200:
            description: Success
    """
    user_service = get_user_service()
    page_size = int(request.args.get("page_size", 50))
    page_number = int(request.args.get("page_number", 1))
    login_stat = user_service.get_login_stat_list(user_id, page_size=page_size, page_number=page_number)
    return jsonify(login_stat), HTTPStatus.OK
