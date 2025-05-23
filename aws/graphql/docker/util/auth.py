import os
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import ExpiredSignatureError, JWTError, jwt

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY') 
BCRYPT_SALT = os.getenv('BCRYPT_SALT').encode('UTF-8') 
ALGORITHM = 'HS256'

def get_current_user(token):
    """
    Validate the JWT generated by this modules create_access_token function.
      It is assumed the phrase "Bearer " is not in the token.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_role: str = payload.get('role')
        if username is None:
            raise ValueError('Could not validate user.')
        return {'user_name': username, 'role': user_role}
    except ExpiredSignatureError:
        raise ValueError('Login has expired.')
    except JWTError:
        raise ValueError('Error occurred validating user.')
    
def create_pwd_hash(password):
    pwd = bcrypt.hashpw(password=password.encode('UTF-8'), salt=BCRYPT_SALT)
    return pwd

def create_access_token(username: str, role: str, expires_delta: timedelta):
    """
    Create a JSON web token.
    """
    encode = {'sub': username, 'role': role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

