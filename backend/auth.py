import os
from functools import wraps

from authlib.integrations.flask_client import OAuth
from flask import redirect, session

from database import find_user_by_id

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:5173")


def login_user(user):
    if not user:
        return False

    session.clear()
    session["user_id"] = str(user.get("id"))
    session["user_email"] = str(user.get("email", ""))
    session["user_name"] = str(user.get("name", ""))
    session["auth_provider"] = str(user.get("auth_provider", "local"))
    return True


def logout_user():
    session.clear()
    return True


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return find_user_by_id(user_id)


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(f"{FRONTEND_URL}/?auth=required")
        return view_func(*args, **kwargs)

    return wrapped


def register_oauth(app):
    oauth = OAuth(app)
    oauth.register(
        name="google",
        client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )
    return oauth
