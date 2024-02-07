from fastapi import FastAPI, status, Response

from src.rinha.models.request import NewTransactionRequest

app = FastAPI()


@app.post("/clientes/{id}/transacoes", status_code=status.HTTP_200_OK, response_class=Response)
async def create_transaction(request: NewTransactionRequest):
    #...
