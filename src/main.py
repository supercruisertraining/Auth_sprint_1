import jwt
from flask import Flask, request, Response, jsonify
from flasgger import Swagger
from user_agents import parse

from schemas.user import UserRegisterModel, UserUpdateModel
from services.user_service import get_user_service
from services.token_service import get_token_service
from services.token_storage_service import get_token_storage_service
from utils.auth import token_required
from core.config import config


app = Flask(__name__)
app.config["SWAGGER"] = {
    "title": "AUTH Service",
    "specs_route": "/docs/",
}
SWAGGER_TEMPLATE = {"securityDefinitions": {"APIKeyHeader": {"type": "apiKey",
                                                             "name": "Authorization",
                                                             "in": "header"}}}
swagger = Swagger(app, template=SWAGGER_TEMPLATE)


@app.route("/api/v1/create_user", methods=["POST"])
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


@app.route("/api/v1/update_user", methods=["PATCH"])
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


@app.route("/api/v1/login", methods=["POST"])
def user_login():
    """
    Войти в систему
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
    user_dto = user_service.login_user(username=request.json["username"], password=request.json["password"])
    if not user_dto:
        return Response(response="Username or password are wrong", status=404)
    token_service = get_token_service(user_id=user_dto.id, user_role=user_dto.role)
    jwt_token_pair = token_service.generate_jwt_key_pair()
    token_storage_service = get_token_storage_service()
    token_storage_service.push_token(user_id=user_dto.id, token_data=jwt_token_pair.refresh_jwt_token)
    user_agent_obj = parse(str(request.user_agent)) if request.user_agent_class else None
    user_service.add_login_record(user_id=user_dto.id,
                                  user_ip=request.remote_addr,
                                  user_os=user_agent_obj.get_os() if user_agent_obj else None,
                                  user_browser=user_agent_obj.get_browser() if user_agent_obj else None,
                                  user_device=user_agent_obj.get_device() if user_agent_obj else None)
    return jsonify(jwt_token_pair.render_to_user()), 200


@app.route("/api/v1/get_login_stat", methods=["GET"])
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


@app.route("/api/v1/refresh", methods=["PUT"])
def refresh_tokens():
    """
    Сменить пару токенов
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
    token_storage_service = get_token_storage_service()
    if not refresh_token:
        return jsonify({"message": "Refresh token was not provided"}), 400
    try:
        user_id = jwt.decode(refresh_token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])["user_id"]
        if not user_id or user_id != token_storage_service.pop_token(refresh_token):
            raise "Strange situation"
    except Exception as e:
        return jsonify({"message": "Problems with refresh token"}), 409
    user_dto = get_user_service().get_user_by_user_id(user_id)
    if not user_dto:
        return jsonify({"message": "No such user"}), 404
    token_service = get_token_service(user_id=user_id, user_role=user_dto.role)
    jwt_token_pair = token_service.generate_jwt_key_pair()
    token_storage_service = get_token_storage_service()
    token_storage_service.push_token(user_id=user_id, token_data=jwt_token_pair.refresh_jwt_token)
    return jsonify(jwt_token_pair.render_to_user()), 200


@app.route("/api/v1/logout", methods=["DELETE"])
@token_required
def logout_user(user_id: str, *args, **kwargs):
    """
    Выйти из системы
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
        204:
            description: Success
    """
    refresh_token = request.json["refresh_token"]
    if refresh_token:
        if user_id != jwt.decode(refresh_token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])["user_id"]:
            return jsonify({"message": "Token not belongs to authenticated user"}), 409
        token_storage_service = get_token_storage_service()
        token_storage_service.pop_token(refresh_token)
    return '', 204


@app.route("/api/v1/logout_hard", methods=["DELETE"])
@token_required
def logout_hard(user_id: str, *args, **kwargs):
    """
    Выйти из системы на всех устройствах
    ---
    security:
      - APIKeyHeader: ['Authorization']
    responses:
        204:
            description: Success
    """
    token_storage_service = get_token_storage_service()
    bg_tokens = token_storage_service.get_tokens_from_background(user_id)
    for token in bg_tokens:
        token_storage_service.pop_token(token)
    return '', 204


@app.route("/api/v1/assign_role", methods=["PATCH"])
@token_required
def assign_role(user_id: str, *args, **kwargs):
    """
    Обновить роль пользователя
    ---
    security:
      - APIKeyHeader: ['Authorization']
    parameters:
      - name: body
        in: body
        schema:
          properties:
            role:
              type: string
    responses:
        204:
            description: Success
    """
    user_service = get_user_service()
    user_service.assign_role(user_id, request.json["role"])
    return '', 204


if __name__ == '__main__':
    app.run()

