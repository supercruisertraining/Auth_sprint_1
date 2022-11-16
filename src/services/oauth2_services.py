from abc import abstractmethod, ABC
from functools import lru_cache
from enum import Enum

import requests
from urllib.parse import urljoin
from authlib.integrations.requests_client import OAuth2Session
import jwt

from services.user_service import get_user_service
from services.token_service import get_token_service
from schemas.user import Oauth2UserInfo, UserModel, UserRegisterModel
from core.config import config


class BaseOauth2Service(ABC):
    social_type = ""
    __redirect_uri = None
    __scope = None
    __discovery_endpoint = None
    __authorization_endpoint = None
    __token_endpoint = None
    __userinfo_endpoint = None
    __client_id = None
    __client_secret = None
    __has_openid = False

    @abstractmethod
    def get_user_data(self, authorization_response_url: str) -> Oauth2UserInfo:
        pass

    def create_user_from_social(self, oauth2_user_info: Oauth2UserInfo) -> UserModel:
        user_service = get_user_service()
        exist_user = user_service.get_user_by_social_id(oauth2_user_info.social_id)
        if exist_user:
            return exist_user
        if oauth2_user_info.username:
            is_valid, reason = user_service.validate_to_create(
                UserRegisterModel(username=oauth2_user_info.username)
            )
            if not is_valid:
                oauth2_user_info.username = None
        new_user_id = user_service.create_user_from_social(username=oauth2_user_info.username,
                                                           external_id=oauth2_user_info.social_id,
                                                           email=oauth2_user_info.email)
        return UserModel(id=new_user_id)

    def get_autorization_url(self) -> tuple[str, str]:
        client = OAuth2Session(client_id=self.__client_id,
                               client_secret=self.__client_secret,
                               scope=self.__scope,
                               redirect_uri=self.__redirect_uri)
        authorization_endpoint = self.__authorization_endpoint
        if self.__discovery_endpoint:
            self.__authorization_endpoint = requests.get(self.__discovery_endpoint).json()["authorization_endpoint"]
        token_service = get_token_service(user_id=None)
        uri, state = client.create_authorization_url(authorization_endpoint,
                                                     state=token_service.generate_oauth2_state(self.social_type))
        return uri, state


class YandexOauth2Service(BaseOauth2Service):
    social_type = "yandex"
    __redirect_uri = urljoin(f"http://{config.API_BASE}", config.OAUTH2_YANDEX_REDIRECT_PATH)
    __scope = config.OAUTH2_YANDEX_SCOPE
    __discovery_endpoint = config.OAUTH2_YANDEX_DISCOVERY_ENDPOINT
    __authorization_endpoint = config.OAUTH2_YANDEX_AUTHORIZATION_ENDPOINT
    __token_endpoint = config.OAUTH2_YANDEX_TOKEN_ENDPOINT
    __userinfo_endpoint = config.OAUTH2_YANDEX_USERINFO_ENDPOINT
    __client_id = config.OAUTH2_YANDEX_CLIENT_ID
    __client_secret = config.OAUTH2_YANDEX_CLIENT_SECRET
    __has_openid = False

    def get_user_data(self, authorization_response_url: str) -> Oauth2UserInfo:
        client = OAuth2Session(client_id=self.__client_id,
                               client_secret=self.__client_secret,
                               redirect_uri=self.__redirect_uri)
        token_data = client.fetch_access_token(url=self.__token_endpoint,
                                               authorization_response=authorization_response_url)
        user_data = requests.get(url=self.__userinfo_endpoint, params={"format": "json"},
                                 headers={"Authorization": f"OAuth {token_data['access_token']}"}).json()
        return Oauth2UserInfo(social_type=self.social_type,
                              social_id=f"{self.social_type}::{user_data['id']}",
                              email=user_data.get("default_email"),
                              username=user_data.get("login"))


class GoogleOauth2Service(BaseOauth2Service):
    social_type = "google"
    __redirect_uri = urljoin(f"http://{config.API_BASE}", config.OAUTH2_GOOGLE_REDIRECT_PATH)
    __scope = config.OAUTH2_GOOGLE_SCOPE
    __discovery_endpoint = config.OAUTH2_GOOGLE_DISCOVERY_ENDPOINT
    __authorization_endpoint = config.OAUTH2_GOOGLE_AUTHORIZATION_ENDPOINT
    __token_endpoint = config.OAUTH2_GOOGLE_TOKEN_ENDPOINT
    __userinfo_endpoint = config.OAUTH2_GOOGLE_USERINFO_ENDPOINT
    __client_id = config.OAUTH2_GOOGLE_CLIENT_ID
    __client_secret = config.OAUTH2_GOOGLE_CLIENT_SECRET
    __has_openid = True

    def get_user_data(self, authorization_response_url: str) -> Oauth2UserInfo:
        discovery_data = requests.get(self.__discovery_endpoint).json()
        self.__token_endpoint = discovery_data["token_endpoint"]
        self.__userinfo_endpoint = discovery_data["userinfo_endpoint"]
        client = OAuth2Session(client_id=self.__client_id,
                               client_secret=self.__client_secret,
                               redirect_uri=self.__redirect_uri)
        token_data = client.fetch_access_token(url=self.__token_endpoint,
                                               authorization_response=authorization_response_url)
        user_data = jwt.decode(token_data["id_token"], options={"verify_signature": False})
        return Oauth2UserInfo(social_type=self.social_type,
                              social_id=f"{self.social_type}::{user_data['sub']}",
                              email=user_data.get("email"),
                              username=user_data.get("login"))


@lru_cache
def get_oauth2_service(social_type: str) -> BaseOauth2Service | None:
    if social_type == YandexOauth2Service.social_type:
        return YandexOauth2Service()
    if social_type == GoogleOauth2Service.social_type:
        return GoogleOauth2Service()


class SocialTypesEnum(Enum):
    yandex = YandexOauth2Service.social_type
    google = GoogleOauth2Service.social_type
