# @spec RF10 - Non-compliant Authentication Service

def get_auth_token():
    # Violation SEC-006: Hardcoded credential token in production code
    password = "supersecretpassword123"
    return password
