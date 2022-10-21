from flask import Flask, request
from flasgger import Swagger

from schemas.user import UserModel
from services.user_service import get_user_service


app = Flask(__name__)
app.config["SWAGGER"] = {
    "title": "AUTH Service",
    "specs_route": "/docs/",
}
swagger = Swagger(app)


@app.route('/hello-world')
def hello_world():
    """
    This function takes a file as input which has sepal length, sepal width, petal length and petal width
    and returns an array of predictions based on the number of data points
    ---
    parameters:
      - name: file
        in: formData
        type: file
        required: true
    responses:
        200:
            description: Success
    """
    return 'Hello, World!'


@app.route("/api/v1/create_user", methods=["POST"])
def create_user():
    """
    This function takes a file as input which has sepal length, sepal width, petal length and petal width
    and returns an array of predictions based on the number of data points
    ---
    parameters:
      - name: file
        in: body
        schema:
          properties:
            username:
              type: string
            password:
              type: string
    responses:
        200:
            description: Success
    """
    new_user = UserModel(**request.json)
    user_service = get_user_service()
    user_service.validate_to_create(new_user)
    user_service.create_user(new_user)

    return ''


if __name__ == '__main__':
    app.run()

