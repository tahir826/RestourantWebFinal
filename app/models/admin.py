from pydantic import BaseModel

class AdminBase(BaseModel):
    name: str
    description: str
    price: float = None  # Optional, used for events


class SubPackage(BaseModel):
    name: str
    price: float


class Package(BaseModel):
    name: str
    price: float
    subpackages: List[SubPackage]


class MenuDisplayInput(BaseModel):
    occasion_id: int
    packages: List[Package]