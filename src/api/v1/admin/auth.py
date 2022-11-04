from http import HTTPStatus

import jwt
from flask import request, jsonify, Blueprint
from user_agents import parse

from services.user_service import get_user_service
from services.token_service import get_token_service
from services.token_storage_service import get_admin_token_storage_service
from utils.auth import admin_token_required
from core.config import config


admin_auth_blueprint_v1 = Blueprint("admin_auth_blueprint_v1", __name__, url_prefix="/admin/api/v1")


@admin_auth_blueprint_v1.route("/login", methods=["POST"])
def user_login():
    """
    Войти в систему, как администратор
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
    user_service = get_user_service()
    user_dto = user_service.login_superuser(username=request.json["username"], password=request.json["password"])
    if not user_dto:
        return jsonify({"message": "Admin username or password are wrong"}), HTTPStatus.NOT_FOUND
    token_service = get_token_service(user_id=user_dto.id)
    jwt_token_pair = token_service.generate_jwt_key_pair(is_admin=True)
    token_storage_service = get_admin_token_storage_service()

    # При входе администратора в систему поддерживаем только одно авторизованное устройство.
    bg_tokens = token_storage_service.get_tokens_from_background(user_dto.id)
    for token in bg_tokens:
        token_storage_service.pop_token(token)

    token_storage_service.push_token(user_id=user_dto.id, token_data=jwt_token_pair.refresh_jwt_token)
    user_agent_obj = parse(str(request.user_agent)) if request.user_agent_class else None
    user_service.add_login_record(user_id=user_dto.id,
                                  user_ip=request.remote_addr,
                                  user_os=user_agent_obj.get_os() if user_agent_obj else None,
                                  user_browser=user_agent_obj.get_browser() if user_agent_obj else None,
                                  user_device=user_agent_obj.get_device() if user_agent_obj else None)
    return jsonify(jwt_token_pair.render_to_user()), HTTPStatus.OK


@admin_auth_blueprint_v1.route("/refresh", methods=["PUT"])
def refresh_tokens():
    """
    Сменить пару токенов для администратора
    ---
    security:
      - APIKeyHeader: ['Authorization']
    parameters:
      - name: body
        in: body
        schema:
          properties:
            refresh_token:
              type: string
    responses:
        200:
            description: Success
        409:
            description: Error
    """
    refresh_token = request.json["refresh_token"]
    token_storage_service = get_admin_token_storage_service()
    if not refresh_token:
        return jsonify({"message": "Refresh token was not provided"}), HTTPStatus.BAD_REQUEST
    try:
        user_id = jwt.decode(refresh_token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])["user_id"]
        if not user_id or user_id != token_storage_service.pop_token(refresh_token):
            raise "Strange situation"
    except Exception as e:
        return jsonify({"message": "Problems with refresh token"}), HTTPStatus.CONFLICT
    user_dto = get_user_service().get_superuser_by_user_id(user_id)
    if not user_dto:
        return jsonify({"message": "No such user"}), HTTPStatus.NOT_FOUND
    token_service = get_token_service(user_id=user_id)
    jwt_token_pair = token_service.generate_jwt_key_pair(is_admin=True)
    token_storage_service = get_admin_token_storage_service()
    token_storage_service.push_token(user_id=user_id, token_data=jwt_token_pair.refresh_jwt_token)
    return jsonify(jwt_token_pair.render_to_user()), HTTPStatus.OK


@admin_auth_blueprint_v1.route("/logout", methods=["DELETE"])
@admin_token_required
def logout_hard(user_id: str, *args, **kwargs):
    """
    Выйти администратору из системы. Выход осуществляется со всех устройств
    ---
    security:
      - APIKeyHeader: ['Authorization']
    responses:
        204:
            description: Success
    """
    token_storage_service = get_admin_token_storage_service()
    bg_tokens = token_storage_service.get_tokens_from_background(user_id)
    for token in bg_tokens:
        token_storage_service.pop_token(token)
    return '', HTTPStatus.NO_CONTENT
