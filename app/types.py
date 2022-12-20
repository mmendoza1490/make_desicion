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


class CampaignResponseData(BaseModel):
    name: str
    id: str
    total: int = 0