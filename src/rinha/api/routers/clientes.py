from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import text

from src.rinha.api.models import NewTransactionRequest
from src.rinha.api.dependencies import (
    DBSessionDep,
    validate_client_id,
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
    async with db:
        client = await db.clients.get(client_id=id)
        try:
            balance = Client.update_balance(
                limit=client.limit,
                current_balance=client.balance,
                new_balance=transaction.value,
                operation_type=request.type,
            )
        except ValueError:
            raise HTTPException(status_code=422, detail="Valor acima do limite.")
        client.balance = balance
        await db.clients.add(client)
        await db.transactions.add(transaction=transaction, client=client)
        await db.session.execute(text("COMMIT"))
        await db.commit()
        await db.refresh(client)
        return {"limite": client.limit, "saldo": client.balance}
