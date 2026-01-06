import json
from urllib.request import urlopen
from functools import wraps
from flask import request, jsonify
from jose import jwt

# Звертаємося до контейнера keycloak по внутрішній мережі docker
KEYCLOAK_URL = "http://keycloak:8080/realms/bike-realm" 

def get_public_key():
    try:
        url = f"{KEYCLOAK_URL}/protocol/openid-connect/certs"
        response = urlopen(url)
        return json.loads(response.read())
    except Exception as e:
        print(f"Auth Error: {e}")
        return None

def require_auth(scope=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get("Authorization", None)
            if not auth_header:
                return jsonify({"error": "No Authorization header"}), 401
            
            token = auth_header.split()[1]
            jwks = get_public_key()
            
            if not jwks:
                return jsonify({"error": "Auth server unavailable"}), 503

            try:
                unverified_header = jwt.get_unverified_header(token)
                rsa_key = next((k for k in jwks["keys"] if k["kid"] == unverified_header["kid"]), None)
                if not rsa_key:
                    raise Exception("Key not found")
                
                payload = jwt.decode(token, rsa_key, algorithms=["RS256"], options={"verify_aud": False})
                
                # Перевірка Scope
                if scope and scope not in payload.get("scope", "").split():
                     return jsonify({"error": "Insufficient Scope"}), 403
                     
            except Exception as e:
                return jsonify({"error": f"Invalid Token: {str(e)}"}), 401
                
            return f(*args, **kwargs)
        return decorated
    return decorator