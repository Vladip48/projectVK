import jwt
import time
from django import template

register = template.Library()

@register.simple_tag
def centrifugo_token(user):
    payload = {
        "sub": str(user.id),
        "exp": int(time.time()) + 3600  # 1 hour expiration
    }
    return jwt.encode(payload, "your-secret-key", algorithm="HS256")