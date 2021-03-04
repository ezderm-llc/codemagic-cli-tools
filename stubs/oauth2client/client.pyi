from collections import namedtuple
from oauth2client import _helpers as _helpers, _pkce as _pkce, clientsecrets as clientsecrets, crypt as crypt, transport as transport
from typing import Any, Optional

HAS_OPENSSL: bool
HAS_CRYPTO: bool
logger: Any
EXPIRY_FORMAT: str
ID_TOKEN_VERIFICATION_CERTS: str
ID_TOKEN_VERIFICATON_CERTS = ID_TOKEN_VERIFICATION_CERTS
OOB_CALLBACK_URN: str
AUTHORIZED_USER: str
SERVICE_ACCOUNT: str
GOOGLE_APPLICATION_CREDENTIALS: str
_CLOUDSDK_CONFIG_DIRECTORY: str
_CLOUDSDK_CONFIG_ENV_VAR: str
ADC_HELP_MSG: Any
_WELL_KNOWN_CREDENTIALS_FILE: str

AccessTokenInfo = namedtuple('AccessTokenInfo', ['access_token', 'expires_in'])
DEFAULT_ENV_NAME: str
NO_GCE_CHECK: Any
GCE_METADATA_TIMEOUT: Any
_SERVER_SOFTWARE: str
_GCE_METADATA_URI: Any
_METADATA_FLAVOR_HEADER: str
_DESIRED_METADATA_FLAVOR: str
_GCE_HEADERS: Any
_UTCNOW: Any
clean_headers: Any
MemoryCache: Any
REFRESH_STATUS_CODES: Any

class SETTINGS:
    env_name: Any = ...

class Error(Exception): ...
class FlowExchangeError(Error): ...
class AccessTokenRefreshError(Error): ...

class HttpAccessTokenRefreshError(AccessTokenRefreshError):
    status: Any = ...
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class TokenRevokeError(Error): ...
class UnknownClientSecretsFlowError(Error): ...
class AccessTokenCredentialsError(Error): ...
class VerifyJwtTokenError(Error): ...
class NonAsciiHeaderError(Error): ...
class ApplicationDefaultCredentialsError(Error): ...
class OAuth2DeviceCodeError(Error): ...
class CryptoUnavailableError(Error, NotImplementedError): ...

def _parse_expiry(expiry: Any): ...

class Credentials:
    NON_SERIALIZED_MEMBERS: Any = ...
    def authorize(self, http: Any) -> None: ...
    def refresh(self, http: Any) -> None: ...
    def revoke(self, http: Any) -> None: ...
    def apply(self, headers: Any) -> None: ...
    def _to_json(self, strip: Any, to_serialize: Optional[Any] = ...): ...
    def to_json(self): ...
    @classmethod
    def new_from_json(cls, json_data: Any): ...
    @classmethod
    def from_json(cls, unused_data: Any): ...

class Flow: ...

class Storage:
    _lock: Any = ...
    def __init__(self, lock: Optional[Any] = ...) -> None: ...
    def acquire_lock(self) -> None: ...
    def release_lock(self) -> None: ...
    def locked_get(self) -> None: ...
    def locked_put(self, credentials: Any) -> None: ...
    def locked_delete(self) -> None: ...
    def get(self): ...
    def put(self, credentials: Any) -> None: ...
    def delete(self): ...

class OAuth2Credentials(Credentials):
    access_token: Any = ...
    client_id: Any = ...
    client_secret: Any = ...
    refresh_token: Any = ...
    store: Any = ...
    token_expiry: Any = ...
    token_uri: Any = ...
    user_agent: Any = ...
    revoke_uri: Any = ...
    id_token: Any = ...
    id_token_jwt: Any = ...
    token_response: Any = ...
    scopes: Any = ...
    token_info_uri: Any = ...
    invalid: bool = ...
    def __init__(self, access_token: Any, client_id: Any, client_secret: Any, refresh_token: Any, token_expiry: Any, token_uri: Any, user_agent: Any, revoke_uri: Optional[Any] = ..., id_token: Optional[Any] = ..., token_response: Optional[Any] = ..., scopes: Optional[Any] = ..., token_info_uri: Optional[Any] = ..., id_token_jwt: Optional[Any] = ...) -> None: ...
    def authorize(self, http: Any): ...
    def refresh(self, http: Any) -> None: ...
    def revoke(self, http: Any) -> None: ...
    def apply(self, headers: Any) -> None: ...
    def has_scopes(self, scopes: Any): ...
    def retrieve_scopes(self, http: Any): ...
    @classmethod
    def from_json(cls, json_data: Any): ...
    @property
    def access_token_expired(self): ...
    def get_access_token(self, http: Optional[Any] = ...): ...
    def set_store(self, store: Any) -> None: ...
    def _expires_in(self): ...
    def _updateFromCredential(self, other: Any) -> None: ...
    def __getstate__(self): ...
    def __setstate__(self, state: Any) -> None: ...
    def _generate_refresh_request_body(self): ...
    def _generate_refresh_request_headers(self): ...
    def _refresh(self, http: Any) -> None: ...
    def _do_refresh_request(self, http: Any) -> None: ...
    def _revoke(self, http: Any) -> None: ...
    def _do_revoke(self, http: Any, token: Any) -> None: ...
    def _retrieve_scopes(self, http: Any) -> None: ...
    def _do_retrieve_scopes(self, http: Any, token: Any) -> None: ...

class AccessTokenCredentials(OAuth2Credentials):
    def __init__(self, access_token: Any, user_agent: Any, revoke_uri: Optional[Any] = ...) -> None: ...
    @classmethod
    def from_json(cls, json_data: Any): ...
    def _refresh(self, http: Any) -> None: ...
    def _revoke(self, http: Any) -> None: ...

def _detect_gce_environment(): ...
def _in_gae_environment(): ...
def _in_gce_environment(): ...

class GoogleCredentials(OAuth2Credentials):
    NON_SERIALIZED_MEMBERS: Any = ...
    def __init__(self, access_token: Any, client_id: Any, client_secret: Any, refresh_token: Any, token_expiry: Any, token_uri: Any, user_agent: Any, revoke_uri: Any = ...) -> None: ...
    def create_scoped_required(self): ...
    def create_scoped(self, scopes: Any): ...
    @classmethod
    def from_json(cls, json_data: Any): ...
    @property
    def serialization_data(self): ...
    @staticmethod
    def _implicit_credentials_from_gae(): ...
    @staticmethod
    def _implicit_credentials_from_gce(): ...
    @staticmethod
    def _implicit_credentials_from_files(): ...
    @classmethod
    def _get_implicit_credentials(cls): ...
    @staticmethod
    def get_application_default(): ...
    @staticmethod
    def from_stream(credential_filename: Any): ...

def _save_private_file(filename: Any, json_contents: Any) -> None: ...
def save_to_well_known_file(credentials: Any, well_known_file: Optional[Any] = ...) -> None: ...
def _get_environment_variable_file(): ...
def _get_well_known_file(): ...
def _get_application_default_credential_from_file(filename: Any): ...
def _raise_exception_for_missing_fields(missing_fields: Any) -> None: ...
def _raise_exception_for_reading_json(credential_file: Any, extra_help: Any, error: Any) -> None: ...
def _get_application_default_credential_GAE(): ...
def _get_application_default_credential_GCE(): ...

class AssertionCredentials(GoogleCredentials):
    assertion_type: Any = ...
    def __init__(self, assertion_type: Any, user_agent: Optional[Any] = ..., token_uri: Any = ..., revoke_uri: Any = ..., **unused_kwargs: Any) -> None: ...
    def _generate_refresh_request_body(self): ...
    def _generate_assertion(self) -> None: ...
    def _revoke(self, http: Any) -> None: ...
    def sign_blob(self, blob: Any) -> None: ...

def _require_crypto_or_die() -> None: ...
def verify_id_token(id_token: Any, audience: Any, http: Optional[Any] = ..., cert_uri: Any = ...): ...
def _extract_id_token(id_token: Any): ...
def _parse_exchange_token_response(content: Any): ...
def credentials_from_code(client_id: Any, client_secret: Any, scope: Any, code: Any, redirect_uri: str = ..., http: Optional[Any] = ..., user_agent: Optional[Any] = ..., token_uri: Any = ..., auth_uri: Any = ..., revoke_uri: Any = ..., device_uri: Any = ..., token_info_uri: Any = ..., pkce: bool = ..., code_verifier: Optional[Any] = ...): ...
def credentials_from_clientsecrets_and_code(filename: Any, scope: Any, code: Any, message: Optional[Any] = ..., redirect_uri: str = ..., http: Optional[Any] = ..., cache: Optional[Any] = ..., device_uri: Optional[Any] = ...): ...

class DeviceFlowInfo:
    @classmethod
    def FromResponse(cls, response: Any): ...

def _oauth2_web_server_flow_params(kwargs: Any): ...

class OAuth2WebServerFlow(Flow):
    client_id: Any = ...
    client_secret: Any = ...
    scope: Any = ...
    redirect_uri: Any = ...
    login_hint: Any = ...
    user_agent: Any = ...
    auth_uri: Any = ...
    token_uri: Any = ...
    revoke_uri: Any = ...
    device_uri: Any = ...
    token_info_uri: Any = ...
    authorization_header: Any = ...
    _pkce: Any = ...
    code_verifier: Any = ...
    params: Any = ...
    def __init__(self, client_id: Any, client_secret: Optional[Any] = ..., scope: Optional[Any] = ..., redirect_uri: Optional[Any] = ..., user_agent: Optional[Any] = ..., auth_uri: Any = ..., token_uri: Any = ..., revoke_uri: Any = ..., login_hint: Optional[Any] = ..., device_uri: Any = ..., token_info_uri: Any = ..., authorization_header: Optional[Any] = ..., pkce: bool = ..., code_verifier: Optional[Any] = ..., **kwargs: Any) -> None: ...
    def step1_get_authorize_url(self, redirect_uri: Optional[Any] = ..., state: Optional[Any] = ...): ...
    def step1_get_device_and_user_codes(self, http: Optional[Any] = ...): ...
    def step2_exchange(self, code: Optional[Any] = ..., http: Optional[Any] = ..., device_flow_info: Optional[Any] = ...): ...

def flow_from_clientsecrets(filename: Any, scope: Any, redirect_uri: Optional[Any] = ..., message: Optional[Any] = ..., cache: Optional[Any] = ..., login_hint: Optional[Any] = ..., device_uri: Optional[Any] = ..., pkce: Optional[Any] = ..., code_verifier: Optional[Any] = ..., prompt: Optional[Any] = ...): ...
