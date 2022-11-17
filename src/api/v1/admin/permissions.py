from http import HTTPStatus

from flask import request, Blueprint, jsonify

from services.user_service import get_user_service
from services.db_service import get_db_service


admin_permissions_blueprint_v1 = Blueprint("admin_permissions_blueprint_v1", __name__, url_prefix="/admin/api/v1")


@admin_permissions_blueprint_v1.route("/check_permission", methods=["GET"])
def has_permission(*args, **kwargs):
    """
    Проверка наличия прав у пользователя на ресурс.
    ---
    security:
      - APIKeyHeader: ['Authorization']
    parameters:
      - name: resource_role_name
        in: query
        type: string
      - name: user_id
        in: query
        type: string
    responses:
        200:
            description: Success
        403:
            description: No permissions
    """
    resource_role_name = request.args["resource_role_name"]
    user_id = request.args["user_id"]
    db_service = get_db_service()
    user_service = get_user_service()
    user_dto = user_service.get_user_by_user_id(user_id)
    resource_role = db_service.get_role(resource_role_name)
    user_role = db_service.get_role(user_dto.role)
    if user_role and user_role.position >= resource_role.position:
        return jsonify({"result": "success"}), HTTPStatus.OK
    return jsonify({"result": "error"}), HTTPStatus.FORBIDDEN
