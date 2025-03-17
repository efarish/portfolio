from db import Base, engine, get_db
from model import User_Location, Users
from sqlalchemy import select, text


def lambda_handler(event, context):
    
    print(f'{event=}')

    for conn in get_db():
        statement = select(text("1"))
        result = conn.execute(statement)
        assert result.one()[0] == 1

    return {'statusCode': 200, 'body': f'Done.'}


def lambda_handler_create_schema(event, context):
    
    print(f'{event=}')

    for conn in get_db():
        statement = select(text("EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"))
        result = conn.execute(statement)
        is_found = result.one()[0] 
        if not is_found:
            print(f'Creating schema...')
            Base.metadata.create_all(bind=engine)
        else: print(f'Schema already exists.')
    
    return {'statusCode': 201, 'body': f'Done.'}

if __name__ == '__main__':
    lambda_handler_create_schema(None, None)

