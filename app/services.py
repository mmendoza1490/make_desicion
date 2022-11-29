import sqlalchemy.orm as _orm
from sqlalchemy import and_

from .database import Database as _database
#import models as _models, schemas as _schemas, database as _database
from .models import TreeDesicion
from .schemas import Schemas as _schemas

from typing import Optional
import numpy
from sklearn.metrics import r2_score

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

    def get_result_regresion(_type):
        try:
            # data 
            x = [1,2,3,5,6,7,8,9,10,12,13,14,15,16,18,19,21,22] # hour
            y = [100,90,80,60,60,55,60,65,70,70,75,76,78,79,90,99,99,100] # count
            mydata = numpy.poly1d(numpy.polyfit(x, y, 3))

            # predict speed
            data=[]
            best_hour={"hour":0, "count":0}
            for hour in range(1,21):
                predict = mydata(hour)
                payload = _schemas.dashboard_regresion(
                    hour=hour,
                    count=predict,
                    _type=_type)

                # get the best
                if predict > best_hour["count"]:
                    best_hour["count"] = int(predict)
                    best_hour["hour"]=hour

                data.append(payload)

            return {
                "error":False,
                "msg":"Response Ok",
                "data":data,
                "bestHour":best_hour["hour"],
                "bestCount":best_hour["count"]
            }
        except Exception as err:
            return {"error":True, "msg":err.args[0], "data":data}
            print (err)