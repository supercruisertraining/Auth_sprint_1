from http import HTTPStatus

from flask import request, Blueprint

from services.user_service import get_user_service
from utils.auth import token_required


roles_blueprint_v1 = Blueprint("roles_blueprint_v1", __name__, url_prefix="/api/v1")


@roles_blueprint_v1.route("/assign_role", methods=["PATCH"])
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
    return '', HTTPStatus.NO_CONTENT
