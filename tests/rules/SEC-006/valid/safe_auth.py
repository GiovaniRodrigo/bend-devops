# @spec RF10 - Safe Authentication Service
import os

def get_auth_token():
    # Compliant: token retrieved from secure environment variable
    return os.environ.get("AUTH_SECRET_TOKEN", "")
