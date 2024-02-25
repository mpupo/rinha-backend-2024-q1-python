from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.rinha.api.dependencies import (
    DBSessionDep,
    validate_client_id,
)
from src.rinha.api.models import NewTransactionRequest
from src.rinha.api.models.response import NewTransactionResponse
from src.rinha.domain.schemas import TransactionCreateSchema

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
    transaction = TransactionCreateSchema(
        client_id=id,
        type=request.type,
        description=request.description,
        value=request.value,
    )
    async with db:
        client = await db.clients.get(client_id=id)
        try:
            client.update_balance(
                new_balance=transaction.value,
                operation_type=request.type,
            )
        except ValueError:
            raise HTTPException(status_code=422, detail="Valor acima do limite.")
        await db.clients.update(client=client)
        await db.transactions.add(transaction=transaction, client=client)
        await db.commit()
    return JSONResponse(
        content=jsonable_encoder({"limite": client.limit, "saldo": client.balance}),
        status_code=status.HTTP_200_OK,
    )
