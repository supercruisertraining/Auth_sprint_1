from http import HTTPStatus

import requests
from flask import request, jsonify, Blueprint
from authlib.integrations.requests_client import OAuth2Session

from services.token_service import get_token_service
from core.config import SocialOauthTypeEnum

auth_social_blueprint_v1 = Blueprint("auth_social_blueprint_v1", __name__, url_prefix="/api/v1")


@auth_social_blueprint_v1.route("/auth_via_social", methods=["GET"])
def get_oauth2_uri():
    """
    Начало аутентификации через сторонние сервисы. Метод возвращает редирект на нужный URI.
    ---
    parameters:
      - name: social_type
        in: query
        type: string
    responses:
        301:
            description: Redirect
    """
    social_type = request.args["social_type"]
    if social_type not in SocialOauthTypeEnum.__members__.keys():
        return jsonify({"error": "No such social type"}), HTTPStatus.NOT_FOUND
    token_service = get_token_service(user_id=None)

    social_type_data = SocialOauthTypeEnum[social_type].value
    print(social_type_data["redirect_uri"])
    client = OAuth2Session(client_id=social_type_data["client_id"],
                           client_secret=social_type_data["client_secret"],
                           scope=social_type_data["scope"],
                           redirect_uri=social_type_data["redirect_uri"])
    authorization_endpoint = social_type_data["authorization_endpoint"]
    if social_type_data["discovery_endpoint"]:
        authorization_endpoint = requests.get(social_type_data["discovery_endpoint"]).json()["authorization_endpoint"]

    if not authorization_endpoint:
        return jsonify({"error": "Something went wrong"}), HTTPStatus.INTERNAL_SERVER_ERROR

    uri, state = client.create_authorization_url(authorization_endpoint,
                                                 state=token_service.generate_oauth2_state(social_type))

    return jsonify({"redirect_url": uri}), HTTPStatus.FOUND


@auth_social_blueprint_v1.route("/social_types", methods=["GET"])
def get_social_types():
    """
    Возвращаются возможные способы Oauth2 аутентификации.
    ---
    responses:
        200:
            description: Список сторонних ресурсов, доступных для Oauth2 аутентификации
    """
    return jsonify({"social_types": list(SocialOauthTypeEnum.__members__.keys())})


@auth_social_blueprint_v1.route("/<string:social_type>/verification_code", methods=["GET"])
# @verify_oauth2_state
def create_or_login_user(social_type: str):
    """
    Метод позволяет через сторонний сервис войти в систему или зарегистрироваться.
    ---
    parameters:
      - name: social_type
        in: path
        type: string
    responses:
        200:
            description: Success
    """
    pass
