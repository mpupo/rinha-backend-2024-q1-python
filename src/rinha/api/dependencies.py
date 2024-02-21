import logging
from typing import Annotated

#from src.rinha.database.orm.session import get_db_session
from src.rinha.database.unit_of_work import get_db_session, AbstractUnitOfWork
from fastapi import Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from src.rinha.database.repository import TransactionRepository, ClientRepository

#DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
DBSessionDep = Annotated[AbstractUnitOfWork, Depends(get_db_session)]


# def create_transaction_repository(db_session: DBSessionDep) -> TransactionRepository:
#     return TransactionRepository(db=db_session)


# def create_client_repository(db_session: DBSessionDep) -> ClientRepository:
#     return ClientRepository(db=db_session)


# TransactionRepositoryDep = Annotated[TransactionRepository, Depends(create_transaction_repository)]
# ClientRepositoryDep = Annotated[ClientRepository, Depends(create_client_repository)]


async def validate_client_id(id: Annotated[int, Path]) -> int:
    VALID_CLIENT_IDS = (1,2,3,4,5)
    if not id in VALID_CLIENT_IDS:
        raise HTTPException(status_code=404, detail="Client not found")
    return id
