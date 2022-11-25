import pydantic as _pydantic

class Schemas:
    class tree_desicion(_pydantic.BaseModel):
        androidid: str
        prediction: str
        date: str

        class Config:
            orm_mode = True

    class linea_regression(_pydantic.BaseModel):
        androidid: str
        hora: str
        date: str

        class Config:
            orm_mode = True