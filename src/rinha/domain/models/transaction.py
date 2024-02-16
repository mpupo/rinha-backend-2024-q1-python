from datetime import datetime
from src.rinha.domain.enums import OperationTypes

from pydantic import BaseModel


class Transaction(BaseModel):
    id: int | None = None
    client_id: int
    type: OperationTypes
    description: str
    created_at: datetime | None = None
