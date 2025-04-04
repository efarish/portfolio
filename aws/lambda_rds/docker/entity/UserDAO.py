from db import get_db
from model import Users


def create(user_name, role, password):
    for conn in get_db():
        create_user_model = Users(
            user_name=user_name,
            role=role,
            password=password)
    conn.add(create_user_model)
    conn.commit()

def create_admin_user():
    for conn in get_db():
        create_user_model = Users(
            user_name='admin',
            role='admin',
            password='a_password_')
        conn.add(create_user_model)
        conn.commit()



