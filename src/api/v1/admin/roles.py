from http import HTTPStatus

from flask import request, Blueprint

from services.user_service import get_user_service
from services.db_service import get_db_service
from utils.auth import admin_token_required


admin_role_blueprint_v1 = Blueprint("admin_role_blueprint_v1", __name__, url_prefix="/admin/api/v1")


@admin_role_blueprint_v1.route("/create_role", methods=["POST"])
@admin_token_required
def create_role(*args, **kwargs):
    """
    Создание роли. Метод доступен только администратору.
        ---
    security:
      - APIKeyHeader: ['Authorization']
    parameters:
      - name: body
        in: body
        schema:
          properties:
            role_name:
              type: string
            position:
              type: integer
            role_description:
              type: string
    responses:
        204:
            description: Success
    """
    role_name = request.json["role_name"]
    role_position = request.json["position"]
    role_description = request.json.get("role_description")
    db_service = get_db_service()
    db_service.admin_create_role(role_name, role_position,  role_description)
    return '', HTTPStatus.NO_CONTENT


@admin_role_blueprint_v1.route("/delete_role", methods=["DELETE"])
@admin_token_required
def delete_role(*args, **kwargs):
    """
    Удаление роли. Метод доступен только администратору.
        ---
    security:
      - APIKeyHeader: ['Authorization']
    parameters:
      - name: body
        in: body
        schema:
          properties:
            role_name:
              type: string
    responses:
        204:
            description: Success
    """
    role_name = request.json["role_name"]
    db_service = get_db_service()
    db_service.admin_delete_role(role_name)
    return '', HTTPStatus.NO_CONTENT


@admin_role_blueprint_v1.route("/update_role", methods=["PATCH"])
@admin_token_required
def update_role(*args, **kwargs):
    """
    Обновление роли. Метод доступен только администратору.
        ---
    security:
      - APIKeyHeader: ['Authorization']
    parameters:
      - name: body
        in: body
        schema:
          properties:
            role_name:
              type: string
            position:
              type: integer
            role_description:
              type: string
    responses:
        204:
            description: Success
    """
    role_name = request.json["role_name"]
    role_position = request.json.get("position")
    role_description = request.json.get("role_description")
    db_service = get_db_service()
    db_service.admin_update_role(role_name, role_position, role_description)
    return '', HTTPStatus.NO_CONTENT


@admin_role_blueprint_v1.route("/assign_role", methods=["PATCH"])
@admin_token_required
def assign_role(*args, **kwargs):
    """
    Назначить роль пользователю. Либо удалить роль у пользователя, если role_name = null.
    ---
    security:
      - APIKeyHeader: ['Authorization']
    parameters:
      - name: body
        in: body
        schema:
          properties:
            user_id:
              type: string
            role_name:
              type: string
    responses:
        204:
            description: Success
    """
    user_service = get_user_service()
    user_service.assign_role(request.json["user_id"], request.json["role_name"])
    return '', HTTPStatus.NO_CONTENT
