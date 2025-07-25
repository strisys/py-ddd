import logging
import os
import threading
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import identity.web
import jwt
from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from jwt import PyJWKClient
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware

# from src.kv_manager import KeyVaultUtility

current_dir = Path(__file__).resolve().parent
dotenv_path = current_dir / '.env'
load_dotenv(dotenv_path)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

AZURE_CLIENT_ID = "AZURE_CLIENT_ID"
AZURE_CLIENT_SECRET = "AZURE_CLIENT_SECRET"
AZURE_TENANT_ID = "AZURE_TENANT_ID"
AZURE_REDIRECT_URI = "AZURE_REDIRECT_URI"
MSAL_DEBUGGING = "MSAL_DEBUGGING"

msal_debugging = (os.getenv(MSAL_DEBUGGING, "false").lower() == "true")
logging.getLogger('msal').setLevel(logging.DEBUG if msal_debugging else logging.INFO)

secret_mapping={"AZURE-CLIENT-ID": AZURE_CLIENT_ID, "AZURE-CLIENT-SECRET": AZURE_CLIENT_SECRET, "AZURE-TENANT-ID": AZURE_TENANT_ID}
# KeyVaultUtility().load_secrets_to_env(secret_mapping=secret_mapping)

assert os.environ.get(AZURE_CLIENT_ID), f"{AZURE_CLIENT_ID} not found in environment variables"
assert os.environ.get(AZURE_CLIENT_SECRET), f"{AZURE_CLIENT_SECRET} not found in environment variables"
assert os.environ.get(AZURE_TENANT_ID), f"{AZURE_TENANT_ID} not found in environment variables"

SESSION_COOKIE_NAME = 'quickstart-fastapi-session-auth'
router = APIRouter()

class InMemorySessionStore:
    def __init__(self):
        self._sessions: dict[str, dict] = {}
        self._lock = threading.Lock()
        self._last_cleanup = datetime.utcnow()

    def get(self, session_id: str) -> tuple[dict, str, bool]:
        session_id = session_id or str(uuid.uuid4())
        is_new = False

        with self._lock:
            if (not self.exists(session_id)):
                self._sessions[session_id] = {}
                is_new = True
            return (self._sessions[session_id], session_id, is_new)

    def exists(self, session_id: str) -> bool:
        return (self._sessions.get(session_id, None) is not None)

    def set(self, session_id: str, data: dict):
        with self._lock:
            self._sessions[session_id] = data

    def cleanup(self, max_age: int = 24 * 60 * 60):
        now = datetime.utcnow()
        if (now - self._last_cleanup) < timedelta(hours=1):
            return
        with self._lock:
            for session_id in list(self._sessions.keys()):
                session = self._sessions[session_id]
                if 'last_accessed' in session:
                    last_accessed = datetime.fromisoformat(session['last_accessed'])
                    if (now - last_accessed).total_seconds() > max_age:
                        del self._sessions[session_id]
            self._last_cleanup = now

class AuthSessionMiddleware(BaseHTTPMiddleware):
    AUTH_SESSION_KEY = 'auth_session_id'

    def __init__(self, app):
        super().__init__(app)
        self.session_store = InMemorySessionStore()

    async def dispatch(self, request, call_next):
        passed_session_id = (request.session.get(AuthSessionMiddleware.AUTH_SESSION_KEY) or '')
        auth_session, session_id, _ = self.session_store.get(passed_session_id)
        request.session[AuthSessionMiddleware.AUTH_SESSION_KEY] = session_id
        request.state.auth_session = auth_session
        original_session = request.state.auth_session.copy()
        response = await call_next(request)
        if (request.state.auth_session != original_session):
            self.session_store.set(session_id, request.state.auth_session)
        return response

class IdentityConfig:
    def __init__(self):
        self.client_id = os.environ.get(AZURE_CLIENT_ID)
        self.client_credential = os.environ.get(AZURE_CLIENT_SECRET)
        self.authority = f"https://login.microsoftonline.com/{os.environ.get(AZURE_TENANT_ID)}"
        self.redirect_uri = os.environ.get(AZURE_REDIRECT_URI)
        self.scopes = ["https://graph.microsoft.com/.default"]
        if (not self.client_id or not self.client_credential or not self.authority or not self.redirect_uri):
            raise ValueError("Missing required identity config environment variables")

class IdentityManager:
    def __init__(self):
        self.config = IdentityConfig()

    def get_inner(self, request: Request) -> identity.web.Auth:
        return identity.web.Auth(session=request.state.auth_session, authority=self.config.authority, client_id=self.config.client_id, client_credential=self.config.client_credential)

    def log_in(self, request: Request):
        inner = self.get_inner(request)
        result = inner.log_in(scopes=self.config.scopes, redirect_uri=self.config.redirect_uri)
        if not "auth_uri" in result:
            raise HTTPException(status_code=500, detail="Failed to initialize login flow")
        return RedirectResponse(url=result["auth_uri"])

    def log_out(self, request: Request):
        pass

    def complete_log_in(self, request: Request):
        params = dict(request.query_params)
        inner = self.get_inner(request)
        result = inner.complete_log_in(params)
        if (len(result) == 0):
            raise HTTPException(status_code=401, detail='failed to exchange authorization code for token')
        return RedirectResponse(url="/", status_code=302)

    def get_user(self, request: Request):
        return self.get_inner(request).get_user()

identity_manager = IdentityManager()

def validate_bearer_token(token: str) -> Optional[dict]:
    try:
        tenant_id = os.getenv(AZURE_TENANT_ID)
        client_id = os.getenv(AZURE_CLIENT_ID)
        audience = f"api://{client_id}"        
        jwks_url = f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"

        logger.warning(f"Validating bearer token validation with audience: {audience} and jwks_url: {jwks_url}")
        signing_key = PyJWKClient(jwks_url).get_signing_key_from_jwt(token)
        decoded = jwt.decode(token, signing_key.key, algorithms=["RS256"], audience=audience)

        return decoded
    except Exception as e:
        logger.warning(f"Bearer token validation failed: {e}")
        return None

@router.route("/login")
async def login(request: Request):
    return identity_manager.log_in(request)

@router.route("/logout")
def logout(request: Request):
    identity_manager.log_out(request)

@router.get('/signin')
def auth_response(request: Request):
    return identity_manager.complete_log_in(request)

async def authenticate(request: Request, call_next):
    public_paths = ["/login", "/signin", "/logout"]

    if any(request.url.path.startswith(path) for path in public_paths):
        return await call_next(request)

    auth_header = request.headers.get("Authorization", "")

    if auth_header.startswith("Bearer "):
        token = auth_header.split("Bearer ")[1]
        user = validate_bearer_token(token)

        if not user:
            raise HTTPException(status_code=401, detail="Invalid bearer token")
        
        request.state.auth_user = user
        return await call_next(request)

    user = identity_manager.get_user(request)

    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    request.state.auth_user = user
    return await call_next(request)

def is_cloud_environment() -> bool:
    val = os.getenv("IS_CLOUD_ENVIRONMENT", '')
    if not val:
        raise ValueError("IS_CLOUD_ENVIRONMENT not set in environment variables")
    return val.lower() == "true"

def configure_pipeline(app: FastAPI) -> FastAPI:
    app.add_middleware(BaseHTTPMiddleware, dispatch=authenticate)
    app.add_middleware(AuthSessionMiddleware)
    app.include_router(router)

    is_cloud = is_cloud_environment()
    secret = os.getenv("SESSION_SECRET", SESSION_COOKIE_NAME)

    cookie_args = {
        'path': "/",
        'domain': None,
        'secret_key': secret,
        'https_only': is_cloud,
        'same_site': "lax",
        'max_age': (3600 * 24),
        'session_cookie': SESSION_COOKIE_NAME,
    }

    app.add_middleware(SessionMiddleware, **cookie_args)
    return app
