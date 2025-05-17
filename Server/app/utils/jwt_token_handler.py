import jwt
from datetime import datetime, timedelta
from flask import current_app

def generate_jwt(user_id, email):
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(seconds=current_app.config['JWT_EXPIRATION_SECONDS'])
    }
    token = jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm="HS256")
    return token
