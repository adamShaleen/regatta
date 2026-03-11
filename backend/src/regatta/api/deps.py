from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from regatta.api.auth import decode_token
from regatta.db.engine import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session


def get_current_user(authorization: Annotated[str, Header()]):
    try:
        token = authorization.split(" ")[1]
        return decode_token(token)
    except IndexError as e:
        raise HTTPException(status_code=401, detail="Missing token") from e
