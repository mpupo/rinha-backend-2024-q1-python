import logging
from typing import Annotated

from src.rinha.database.orm.session import get_db_session
from fastapi import Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from src.rinha.database.transaction_repository import TransactionRepository, ClientRepository

DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]


def create_transaction_repository(db_session: DBSessionDep) -> TransactionRepository:
    return TransactionRepository(db=db_session)


def create_client_repository(db_session: DBSessionDep) -> ClientRepository:
    return ClientRepository(db=db_session)


TransactionRepositoryDep = Annotated[TransactionRepository, Depends(create_transaction_repository)]
ClientRepositoryDep = Annotated[ClientRepository, Depends(create_client_repository)]


async def validate_client_id(id: Annotated[int, Path], client_repository: ClientRepositoryDep) -> int:
    logging.info(f"Recebeu: client_id[{id}]")
    if not await client_repository.get(client_id=id):
        raise HTTPException(status_code=404, detail="Client not found")
    return id
