from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError

SECRET_KEY: str = "aboba"
ALGORITHM: str = "HS256"

class UtilsService:
    @staticmethod
    def decode_jwt(token: str) -> dict:
        try:
            # Расшифровка токена
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except ExpiredSignatureError:
            raise ValueError("Срок действия токена истёк.")
        except JWTError:
            raise ValueError("Невалидный токен.")