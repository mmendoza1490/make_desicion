from gettext import Catalog
import os
from re import template
from typing import Optional

import sqlalchemy.orm as _orm
from sqlalchemy import and_
from psycopg2 import connect, extras
import numpy
from sklearn.metrics import r2_score

from .database import Database as _database
from .models import TreeDesicion
from .schemas import Schemas as _schemas

from app.types import Response, Catalogs

class Data_base:
    def create_database():
        return _database.Base.metadata.create_all(bind=_database.engine)

    def get_db():
        db = _database.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def connect():
        return connect(
            database=os.getenv("PSQL_DB"),
            user=os.getenv("USER_DB"),
            password=os.getenv("PASS_DB"),
            host=os.getenv("HOST_DB"),
            port=os.getenv("PORT_DB"),
            cursor_factory=extras.NamedTupleCursor
        )


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


class query:
    def __init__(self) -> None:
        pass

    def brands(self,DbConnection):
        try:
            with DbConnection as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT 
                            id, 
                            oem_role name
                        FROM public.oem
                        """
                    )
                    brands = cursor.fetchall()
            data=[Catalogs(id=brand.id, name=brand.name) for brand in brands]
            error = False
            msg = ""
        except Exception as e:
            error = True
            msg = e.__str__()
            data = []

        return Response(
            msg=msg,
            error=error,
            data=data
        )

    def countries(self,DbConnection):
        try:
            with DbConnection as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT mcc, country as name 
                        FROM users_admin.countries 
                        WHERE show = true
                        ORDER BY name
                        """
                    )
                    countries = cursor.fetchall()
            data=[Catalogs(id=country.mcc, name=country.name) for country in countries]
            error = False
            msg = ""
        except Exception as e:
            error = True
            msg = e.__str__()
            data = []

        return Response(
            msg=msg,
            error=error,
            data=data
        )

    def template(self, DbConnection):
        try:
            with DbConnection as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        with tmp_used as (
                        select distinct template_id from update
                        )
                        select id, template_key as key
                        from cota_campaign_templates  tmp 
                        inner join tmp_used tused 
                        on (tmp.id=tused.template_id)
                        order by tmp.id
                        """
                    )
                    template_ = cursor.fetchall()
            data=[Catalogs(id=tmp.id, name=tmp.key) for tmp in template_]
            error = False
            msg = ""
        except Exception as e:
            error = True
            msg = e.__str__()
            data = []

        return Response(
            msg=msg,
            error=error,
            data=data
        )