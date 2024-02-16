from pydantic import BaseModel


class Client(BaseModel):
    id: int | None = None
    limit: int
    initial_value: int = 0
