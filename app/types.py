from typing import List

from pydantic import BaseModel


class Brand(BaseModel):
    id: int
    name: str


class BrandResponse(BaseModel):
    error: bool
    msg: str
    data: List[Brand]


class Country(BaseModel):
    mcc: str
    name: str


class CountryResponse(BaseModel):
    error: bool
    msg: str
    data: List[Country]
