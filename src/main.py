from flask import Flask, request, Response, jsonify
from flasgger import Swagger

from schemas.user import UserRegisterModel
from services.user_service import get_user_service
from services.token_service import get_token_service
from services.token_storage_service import BaseTokenStorage, get_token_storage_service


app = Flask(__name__)
app.config["SWAGGER"] = {
    "title": "AUTH Service",
    "specs_route": "/docs/",
}
swagger = Swagger(app)


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
        return Response(response=reason, status=409)
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


if __name__ == '__main__':
    app.run()

