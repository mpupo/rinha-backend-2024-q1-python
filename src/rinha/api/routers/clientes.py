import logging
from fastapi import APIRouter, status, Response, Depends, HTTPException

from src.rinha.api.models import NewTransactionRequest
from src.rinha.api.dependencies import (
    DBSessionDep,
    # TransactionRepositoryDep,
    validate_client_id,
    # ClientRepositoryDep,
)
from src.rinha.api.models.response import NewTransactionResponse
from src.rinha.domain.models import Transaction, Client


router = APIRouter(
    prefix="/clientes",
    tags=["clientes"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(validate_client_id)],
)


@router.post(
    "/{id}/transacoes",
    status_code=status.HTTP_200_OK,
    response_model=NewTransactionResponse,
)
async def create_transaction(
    id: int,
    request: NewTransactionRequest,
    db: DBSessionDep,
):
    transaction = Transaction(
        client_id=id,
        type=request.type,
        description=request.description,
        value=request.value,
    )
    async with db as db:
        client = await db.clients.get(client_id=id)
        try:
            balance = Client.update_balance(
                limit=client.limite,
                current_balance=client.saldo,
                new_balance=transaction.value, 
                operation_type=request.type
            )
        except ValueError:
            raise HTTPException(status_code=422, detail="Valor acima do limite.")
        updated_client = await db.clients.update_balance(client_id=client.id, balance=balance) 
        await db.transactions.add(transaction=transaction, client=updated_client)
        await db.commit()
        return {"limite": client.limite, "saldo": client.saldo}
