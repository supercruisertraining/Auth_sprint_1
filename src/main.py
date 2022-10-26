import jwt
from flask import Flask, request, Response, jsonify
from flasgger import Swagger

from schemas.user import UserRegisterModel
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
    user_service.create_user(new_user)

    return Response(response="User created", status=200)


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
    return jsonify(jwt_token_pair.render_to_user()), 200


@app.route("/api/v1/refresh", methods=["PUT"])
def refresh_tokens():
    """
    Сменить пару токенов
    ---
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


if __name__ == '__main__':
    app.run()

