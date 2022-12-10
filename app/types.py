from gettext import Catalog
from typing import List

from pydantic import BaseModel


class Catalogs(BaseModel):
    id: str
    name: str


class Response(BaseModel):
    error: bool
    msg: str
    data: List[Catalogs]