from http import HTTPStatus

import requests
from flask import request, jsonify, Blueprint
from authlib.integrations.requests_client import OAuth2Session
from user_agents import parse

from schemas.user import UserRegisterModel
from services.token_service import get_token_service
from services.token_storage_service import get_token_storage_service
from services.user_service import get_user_service
from core.config import SocialOauthTypeEnum
from utils.auth import verify_oauth2_state, get_openid_data, get_userinfo_data

auth_social_blueprint_v1 = Blueprint("auth_social_blueprint_v1", __name__, url_prefix="/api/v1/auth_social")


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
@verify_oauth2_state
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
    social_type_data = SocialOauthTypeEnum[social_type].value
    token_endpoint = social_type_data["token_endpoint"]
    userinfo_endpoint = social_type_data["userinfo_endpoint"]
    if social_type_data["discovery_endpoint"]:
        discovery_data = requests.get(social_type_data["discovery_endpoint"]).json()
        token_endpoint = discovery_data["token_endpoint"]
        userinfo_endpoint = discovery_data["userinfo_endpoint"]
    client = OAuth2Session(client_id=social_type_data["client_id"],
                           client_secret=social_type_data["client_secret"],
                           redirect_uri=social_type_data["redirect_uri"])
    token_data = client.fetch_access_token(url=token_endpoint, authorization_response=request.url)
    if social_type_data["openid"]:
        external_user_id, email, username = get_openid_data(token_data)
    else:
        external_user_id, email, username = get_userinfo_data(token_data, userinfo_endpoint)
    social_id = f"{social_type}::{external_user_id}"
    user_service = get_user_service()
    exist_user = user_service.get_user_by_social_id(social_id)
    #  Если пользователя нет - создаём.
    if not exist_user:
        if username:
            is_valid, reason = user_service.validate_to_create(UserRegisterModel(username=username))
            if not is_valid:
                username = None
        new_user_id = user_service.create_user_from_social(username=username, external_id=social_id, email=email)
    else:
        new_user_id = exist_user.id

    # Делаем вход в пользователя систему
    token_service = get_token_service(user_id=new_user_id)
    jwt_token_pair = token_service.generate_jwt_key_pair(user_role=exist_user.role if exist_user else None)
    token_storage_service = get_token_storage_service()
    token_storage_service.push_token(user_id=new_user_id, token_data=jwt_token_pair.refresh_jwt_token)
    user_agent_obj = parse(str(request.user_agent)) if request.user_agent_class else None
    user_service.add_login_record(user_id=new_user_id,
                                  user_ip=request.remote_addr,
                                  user_os=user_agent_obj.get_os() if user_agent_obj else None,
                                  user_browser=user_agent_obj.get_browser() if user_agent_obj else None,
                                  user_device=user_agent_obj.get_device() if user_agent_obj else None)
    return jsonify(jwt_token_pair.render_to_user()), HTTPStatus.OK



