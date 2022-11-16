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
    _redirect_uri = None
    _scope = None
    _discovery_endpoint = None
    _authorization_endpoint = None
    _token_endpoint = None
    _userinfo_endpoint = None
    _client_id = None
    _client_secret = None
    _has_openid = False

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
        client = OAuth2Session(client_id=self._client_id,
                               client_secret=self._client_secret,
                               scope=self._scope,
                               redirect_uri=self._redirect_uri)
        if self._discovery_endpoint:
            self._authorization_endpoint = requests.get(self._discovery_endpoint).json()["authorization_endpoint"]
        token_service = get_token_service(user_id=None)
        uri, state = client.create_authorization_url(url=self._authorization_endpoint,
                                                     state=token_service.generate_oauth2_state(self.social_type))
        return uri, state


class YandexOauth2Service(BaseOauth2Service):
    social_type = "yandex"

    def __init__(self):
        self._redirect_uri = urljoin(f"http://{config.API_BASE}", config.OAUTH2_YANDEX_REDIRECT_PATH)
        self._scope = config.OAUTH2_YANDEX_SCOPE
        self._discovery_endpoint = config.OAUTH2_YANDEX_DISCOVERY_ENDPOINT
        self._authorization_endpoint = config.OAUTH2_YANDEX_AUTHORIZATION_ENDPOINT
        self._token_endpoint = config.OAUTH2_YANDEX_TOKEN_ENDPOINT
        self._userinfo_endpoint = config.OAUTH2_YANDEX_USERINFO_ENDPOINT
        self._client_id = config.OAUTH2_YANDEX_CLIENT_ID
        self._client_secret = config.OAUTH2_YANDEX_CLIENT_SECRET
        self._has_openid = False

    def get_user_data(self, authorization_response_url: str) -> Oauth2UserInfo:
        client = OAuth2Session(client_id=self._client_id,
                               client_secret=self._client_secret,
                               redirect_uri=self._redirect_uri)
        token_data = client.fetch_access_token(url=self._token_endpoint,
                                               authorization_response=authorization_response_url)
        user_data = requests.get(url=self._userinfo_endpoint, params={"format": "json"},
                                 headers={"Authorization": f"OAuth {token_data['access_token']}"}).json()
        return Oauth2UserInfo(social_type=self.social_type,
                              social_id=f"{self.social_type}::{user_data['id']}",
                              email=user_data.get("default_email"),
                              username=user_data.get("login"))


class GoogleOauth2Service(BaseOauth2Service):
    social_type = "google"

    def __init__(self):
        self._redirect_uri = urljoin(f"http://{config.API_BASE}", config.OAUTH2_GOOGLE_REDIRECT_PATH)
        self._scope = config.OAUTH2_GOOGLE_SCOPE
        self._discovery_endpoint = config.OAUTH2_GOOGLE_DISCOVERY_ENDPOINT
        self._authorization_endpoint = config.OAUTH2_GOOGLE_AUTHORIZATION_ENDPOINT
        self._token_endpoint = config.OAUTH2_GOOGLE_TOKEN_ENDPOINT
        self._userinfo_endpoint = config.OAUTH2_GOOGLE_USERINFO_ENDPOINT
        self._client_id = config.OAUTH2_GOOGLE_CLIENT_ID
        self._client_secret = config.OAUTH2_GOOGLE_CLIENT_SECRET
        self._has_openid = True

    def get_user_data(self, authorization_response_url: str) -> Oauth2UserInfo:
        discovery_data = requests.get(self._discovery_endpoint).json()
        self._token_endpoint = discovery_data["token_endpoint"]
        self._userinfo_endpoint = discovery_data["userinfo_endpoint"]
        client = OAuth2Session(client_id=self._client_id,
                               client_secret=self._client_secret,
                               redirect_uri=self._redirect_uri)
        token_data = client.fetch_access_token(url=self._token_endpoint,
                                               authorization_response=authorization_response_url)
        user_data = jwt.decode(token_data["id_token"], options={"verify_signature": False})
        return Oauth2UserInfo(social_type=self.social_type,
                              social_id=f"{self.social_type}::{user_data['sub']}",
                              email=user_data.get("email"),
                              username=user_data.get("email").split("@")[0] if user_data.get("email") else None)


@lru_cache
def get_oauth2_service(social_type: str) -> BaseOauth2Service | None:
    if social_type == YandexOauth2Service.social_type:
        return YandexOauth2Service()
    if social_type == GoogleOauth2Service.social_type:
        return GoogleOauth2Service()


class SocialTypesEnum(Enum):
    yandex = YandexOauth2Service.social_type
    google = GoogleOauth2Service.social_type
