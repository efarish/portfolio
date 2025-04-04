import logging
import os

from db import Base, engine, get_db
from sqlalchemy import select, text

logger = logging.getLogger(__name__)

def create_schema():

    for conn in get_db():
        sql = os.getenv('SCHEMA_CHECK')
        statement = select(text(sql))
        result = conn.execute(statement)
        is_found = result.one()[0] 
        if not is_found:
            logger.info(f'Creating schema...')
            Base.metadata.create_all(bind=engine)
        else: logger.info(f'Schema already exists.')