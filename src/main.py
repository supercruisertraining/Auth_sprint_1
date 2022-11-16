from http import HTTPStatus

from flask import Flask, request
from flasgger import Swagger
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

from api.v1.users import users_blueprint_v1
from api.v1.auth import auth_blueprint_v1
from api.v1.roles import roles_blueprint_v1
from api.v1.admin.auth import admin_auth_blueprint_v1
from api.v1.admin.roles import admin_role_blueprint_v1
from api.v1.admin.permissions import admin_permissions_blueprint_v1
from api.v1.auth_social import auth_social_blueprint_v1
from utils.cli_admin import admin_cli_blueprint
from core.config import config


app = Flask(__name__)
app.register_blueprint(users_blueprint_v1)
app.register_blueprint(auth_blueprint_v1)
app.register_blueprint(roles_blueprint_v1)
app.register_blueprint(auth_social_blueprint_v1)

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


@app.before_request
def before_request():
    if config.DO_TRACE:
        request_id = request.headers.get('X-Request-Id')
        if not request_id:
            raise RuntimeError('Request id is required')


def configure_tracer() -> None:
    trace.set_tracer_provider(TracerProvider(resource=Resource.create({SERVICE_NAME: "AUTH"})))
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=config.JAEGER_HOST,
                agent_port=config.JAEGER_PORT,
            )
        )
    )


if __name__ == '__main__':
    if config.DO_TRACE:
        configure_tracer()
        FlaskInstrumentor().instrument_app(app)
    app.run()

