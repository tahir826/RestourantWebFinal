from pydantic import BaseModel

class AdminBase(BaseModel):
    name: str
    description: str
    price: float = None  # Optional, used for events