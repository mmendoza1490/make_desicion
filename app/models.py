import datetime as _dt
import sqlalchemy as _sql
import sqlalchemy.orm as _orm

#import database as _database
from .database import Database as _database


class DecisionTree(_database.Base):
    __tablename__ = "decision_tree"
    androidid = _sql.Column(_sql.String, primary_key=True, index=True)
    decision = _sql.Column(_sql.String)
    date = _sql.Column(_sql.String)

class LineaRegression(_database.Base):
    __tablename__ = "linea_regression"
    androidid = _sql.Column(_sql.String, primary_key=True, index=True)
    hora = _sql.Column(_sql.Integer)
    date = _sql.Column(_sql.String)