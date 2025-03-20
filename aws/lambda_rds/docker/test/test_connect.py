import pytest
from db import get_async_db
from sqlalchemy import text
from sqlalchemy.future import select


@pytest.mark.asyncio(loop_scope="function")
async def test_select_dual():
    async for db in get_async_db():
        statement = select(text("1"))
        result = await db.execute(statement)
        assert result.one()[0] == 1



