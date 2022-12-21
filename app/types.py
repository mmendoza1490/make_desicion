from gettext import Catalog
from typing import List, Optional

from pydantic import BaseModel


class Catalogs(BaseModel):
    id: str
    name: str


class Response(BaseModel):
    error: bool
    msg: str
    data: List[Catalogs]


class DecisionTreeData(BaseModel):
    name: str
    total: int = 0


class DecisionTreeResponse(BaseModel):
    error: bool
    msg: str
    data: List[DecisionTreeData]