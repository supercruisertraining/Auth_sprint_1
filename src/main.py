from flask import Flask
from flasgger import Swagger

from api.v1.users import users_blueprint_v1
from api.v1.auth import auth_blueprint_v1


app = Flask(__name__)
app.register_blueprint(users_blueprint_v1)
app.register_blueprint(auth_blueprint_v1)
app.config["SWAGGER"] = {
    "title": "AUTH Service",
    "specs_route": "/docs/",
}
SWAGGER_TEMPLATE = {"securityDefinitions": {"APIKeyHeader": {"type": "apiKey",
                                                             "name": "Authorization",
                                                             "in": "header"}}}
swagger = Swagger(app, template=SWAGGER_TEMPLATE)


if __name__ == '__main__':
    app.run()

