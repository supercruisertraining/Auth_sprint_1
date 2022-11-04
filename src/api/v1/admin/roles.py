from http import HTTPStatus

from flask import request, Blueprint

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
    responses:
        204:
            description: Success
    """
    role_name = request.json["role_name"]
    db_service = get_db_service()
    db_service.admin_create_role(role_name)
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
