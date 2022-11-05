from http import HTTPStatus

from flask import Flask
from flasgger import Swagger

from api.v1.users import users_blueprint_v1
from api.v1.auth import auth_blueprint_v1
from api.v1.roles import roles_blueprint_v1
from api.v1.admin.auth import admin_auth_blueprint_v1
from api.v1.admin.roles import admin_role_blueprint_v1
from api.v1.admin.permissions import admin_permissions_blueprint_v1
from utils.cli_admin import admin_cli_blueprint


app = Flask(__name__)
app.register_blueprint(users_blueprint_v1)
app.register_blueprint(auth_blueprint_v1)
app.register_blueprint(roles_blueprint_v1)

# Admin
app.register_blueprint(admin_cli_blueprint)
app.register_blueprint(admin_auth_blueprint_v1)
app.register_blueprint(admin_role_blueprint_v1)
app.register_blueprint(admin_permissions_blueprint_v1)
app.config["SWAGGER"] = {
    "title": "AUTH Service",
    "specs_route": "/docs/",
}
SWAGGER_TEMPLATE = {"securityDefinitions": {"APIKeyHeader": {"type": "apiKey",
                                                             "name": "Authorization",
                                                             "in": "header"}}}
swagger = Swagger(app, template=SWAGGER_TEMPLATE)


@app.route("/health_check", methods=["GET"])
def health_check():
    return '', HTTPStatus.NO_CONTENT


if __name__ == '__main__':
    app.run()

