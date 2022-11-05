from flask import Blueprint, jsonify

from services.db_service import get_db_service


roles_blueprint_v1 = Blueprint("roles_blueprint_v1", __name__, url_prefix="/api/v1")


@roles_blueprint_v1.route("/get_roles", methods=["GET"])
def get_roles_list():
    """
    Получить с список существующих ролей. Доступно анонимным пользователям.
    ---
    responses:
        200:
            description: Success
    """
    db_service = get_db_service()
    roles_list = db_service.get_roles_list()
    return jsonify([role.__dict__ for role in roles_list])
