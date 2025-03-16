from db import get_db
from sqlalchemy import select, text


def lambda_handler(event, context):
    print(f'{event=}')

    for conn in get_db():
        statement = select(text("1"))
        result = conn.execute(statement)
        assert result.one()[0] == 1

    return {'statusCode': 200, 'body': f'Done.'}

