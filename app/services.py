import sqlalchemy.orm as _orm
from sqlalchemy import and_

from .database import Database as _database
#import models as _models, schemas as _schemas, database as _database
from .models import TreeDesicion
from .schemas import Schemas as _schemas

from typing import Optional

class Data_base:
    def create_database():
        return _database.Base.metadata.create_all(bind=_database.engine)

    def get_db():
        db = _database.SessionLocal()
        try:
            yield db
        finally:
            db.close()

class Service:
    def get_result_tree(db: _orm.Session):
        return None