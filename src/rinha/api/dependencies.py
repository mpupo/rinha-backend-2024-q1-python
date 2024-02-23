from typing import Annotated

from fastapi import Depends, HTTPException, Path

from src.rinha.database.unit_of_work import AbstractUnitOfWork, get_db_session

DBSessionDep = Annotated[AbstractUnitOfWork, Depends(get_db_session)]


async def validate_client_id(id: Annotated[int, Path]) -> int:
    VALID_CLIENT_IDS = (1, 2, 3, 4, 5)
    if id not in VALID_CLIENT_IDS:
        raise HTTPException(status_code=404, detail="Client not found")
    return id
