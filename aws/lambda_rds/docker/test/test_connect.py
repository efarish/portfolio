import pytest
from sqlalchemy import text
from sqlalchemy.future import select

from .util import *


@pytest.mark.asyncio(loop_scope="function")
async def test_select_dual():

    async with TestSessionLocal_Async() as db:
        statement = select(text("1"))
        result = await db.execute(statement)
        assert result.one()[0] == 1



