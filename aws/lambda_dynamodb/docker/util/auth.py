import os
from datetime import datetime, timedelta, timezone

import bcrypt
from entity import UsersDAO
from jose import JWTError, jwt

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY') 
BCRYPT_SALT = os.getenv('BCRYPT_SALT').encode('UTF-8') 
ALGORITHM = 'HS256'

def get_current_user(token):

    print(f'JWT Token in current user: {token=}')

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_role: str = payload.get('role')
        if username is None:
            raise ValueError('Could not validate user.')
        return {'user_name': username, 'role': user_role}
    except JWTError:
        raise ValueError('Error occurred validating user.')
    
def create_pwd_hash(password):
    pwd = bcrypt.hashpw(password=password.encode('UTF-8'), salt=BCRYPT_SALT)
    return pwd

def check_user_name(username: str):

    try:
        user: UsersDAO.User = UsersDAO.get_user(username,True)
    except ValueError:
        return None
    
    return user 

def authenticate_user(username: str, password: str):
    user = check_user_name(username) 
    if not user:
        return False
    #check = bcrypt.checkpw(password=password.encode('UTF-8'), hashed_password=user.password)
    check = create_pwd_hash(password).decode('UTF-8') == user.password
    if not check:
        return False
    return user

def create_access_token(username: str, role: str, expires_delta: timedelta):
    encode = {'sub': username, 'role': role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

def login_for_access_token(username, password):
    """
    Authenticate user, generate and return JWT.
    """
    user = authenticate_user(username, password)
    if not user:
        raise ValueError('Could not validate user.')
    token = create_access_token(user.user_name, user.role, timedelta(minutes=1440))

    return token