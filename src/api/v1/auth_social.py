from http import HTTPStatus

from flask import request, jsonify, Blueprint
from user_agents import parse

from services.token_service import get_token_service
from services.token_storage_service import get_token_storage_service
from services.user_service import get_user_service
from services.oauth2_services import get_oauth2_service, SocialTypesEnum
from utils.auth import verify_oauth2_state

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
    oauth2_service = get_oauth2_service(social_type)
    if not oauth2_service:
        return jsonify({"error": "No such social type"}), HTTPStatus.NOT_FOUND

    uri, _ = oauth2_service.get_autorization_url()

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
    return jsonify([e.value for e in SocialTypesEnum])


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
    oauth2_service = get_oauth2_service(social_type)
    oauth2_user_data = oauth2_service.get_user_data(authorization_response_url=request.url)
    new_or_existing_user = oauth2_service.create_user_from_social(oauth2_user_data)

    # Делаем вход в пользователя систему
    token_service = get_token_service(user_id=new_or_existing_user.id)
    jwt_token_pair = token_service.generate_jwt_key_pair(user_role=new_or_existing_user.role)
    token_storage_service = get_token_storage_service()
    token_storage_service.push_token(user_id=new_or_existing_user.id, token_data=jwt_token_pair.refresh_jwt_token)
    user_agent_obj = parse(str(request.user_agent)) if request.user_agent_class else None

    user_service = get_user_service()
    user_service.add_login_record(user_id=new_or_existing_user.id,
                                  user_ip=request.remote_addr,
                                  user_os=user_agent_obj.get_os() if user_agent_obj else None,
                                  user_browser=user_agent_obj.get_browser() if user_agent_obj else None,
                                  user_device=user_agent_obj.get_device() if user_agent_obj else None)
    return jsonify(jwt_token_pair.render_to_user()), HTTPStatus.OK
