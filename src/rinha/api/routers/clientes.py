from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import ORJSONResponse

from src.rinha.api.dependencies import (
    DBSessionDep,
    validate_client_id,
)
from src.rinha.api.models import NewTransactionRequest
from src.rinha.api.models.response import (
    BalanceDTO,
    # NewTransactionResponse,
    # QueryTransactionsResponse,
    TransactionsDTO,
)
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
    # response_model=NewTransactionResponse,
    response_class=ORJSONResponse,
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
    return ORJSONResponse(
        content={"limite": client.limit, "saldo": client.balance},
        status_code=status.HTTP_200_OK,
    )


@router.get(
    "/{id}/extrato",
    status_code=status.HTTP_200_OK,
    # response_model=QueryTransactionsResponse,
    response_class=ORJSONResponse,
)
async def list_transactions(
    id: int,
    db: DBSessionDep,
):
    async with db:
        client = await db.clients.get(client_id=id, with_transactions=True)

    balance = BalanceDTO(total=client.balance, limit=client.limit)
    transactions = tuple(
        TransactionsDTO.model_validate(transaction).model_dump(by_alias=True)
        for transaction in client.transactions
    )

    return {
        "saldo": balance.model_dump(by_alias=True),
        "ultimas_transacoes": transactions,
    }
    # return QueryTransactionsResponse(balance=balance, recent_transactions=transactions)
