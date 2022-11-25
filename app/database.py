import sqlalchemy as _sql
import sqlalchemy.ext.declarative as _declarative
import sqlalchemy.orm as _orm
import os
from dotenv import load_dotenv
load_dotenv(override=True)
SQLALCHEMY_DATABASE_URL = "sqlite:///./result_mbd.db"

class Database:
    engine = _sql.create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )

    SessionLocal = _orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base = _declarative.declarative_base()