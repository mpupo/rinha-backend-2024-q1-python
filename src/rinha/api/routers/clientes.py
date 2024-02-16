import logging
from fastapi import APIRouter, status, Response, Depends

from src.rinha.api.models import NewTransactionRequest
from src.rinha.api.dependencies import DBSessionDep, TransactionRepositoryDep, validate_client_id
from src.rinha.domain.models import Transaction


router = APIRouter(
    prefix="/clientes",
    tags=["clientes"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/{id}/transacoes", status_code=status.HTTP_200_OK, response_class=Response, dependencies=[Depends(validate_client_id)]
)
async def create_transaction(id: int, request: NewTransactionRequest, repository: TransactionRepositoryDep):
    logging.info(f"Recebendo transacao: ID[{id}], dados[{request}]")
    transaction = Transaction(
        client_id=id,
        type=request.type,
        description=request.description
    )
    await repository.add(transaction=transaction)
    return Response(status_code=status.HTTP_200_OK)
