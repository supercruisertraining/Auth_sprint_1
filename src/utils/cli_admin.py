import click
from flask import Blueprint

from services.user_service import get_user_service
from schemas.user import SuperUserCreationModel

admin_cli_blueprint = Blueprint('admin_cli', __name__)


@admin_cli_blueprint.cli.command("create_superuser")
@click.argument("username", type=str, required=True)
@click.password_option()
@click.option("--first_name")
@click.option("--last_name")
def create_superuser_cli(username: str, password: str, first_name: str = "", last_name: str = ""):
    """Creates a superuser"""
    return create_superuser(username, password, first_name, last_name)


def create_superuser(username: str, password: str, first_name: str = "", last_name: str = ""):
    """Creates a superuser"""
    super_user = SuperUserCreationModel(username=username, password=password,
                                        first_name=first_name, last_name=last_name)
    user_service = get_user_service()
    is_valid, reason = user_service.validate_to_create_superuser(super_user)
    if not is_valid:
        print(reason, "\nOperation stopped.")
        return
    super_user_id = user_service.create_superuser(super_user)
    print(f"Superuser {username} created successfully!\nSuperUser ID: {super_user_id}")
    return super_user_id


@admin_cli_blueprint.cli.command("list_superusers")
def list_superusers():
    """List existing superusers"""
    user_service = get_user_service()
    super_users_list = user_service.get_superusers()
    if not super_users_list:
        print("No superusers")
    print("\n".join(map(lambda user:
                        " ".join(el for el in [str(user.id), user.username, user.first_name, user.last_name] if el),
                        super_users_list)))
