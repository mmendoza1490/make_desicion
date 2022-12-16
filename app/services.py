from dataclasses import dataclass
import os
from datetime import datetime as dt
import sqlalchemy.orm as _orm
from sqlalchemy import and_
from psycopg2 import connect, extras, sql
import numpy
from sklearn.metrics import r2_score
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

from .database import Database as _database
from .models import TreeDesicion
from .schemas import Schemas as _schemas

from app.types import Response, Catalogs

@dataclass
class Data_base():
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
    def __init__(self) -> None:
        self.query = query()

    def get_result_tree(self, db: _orm.Session):
        return None

    def get_result_regresion(self, dbConnection, type_, date_, mcc):
        try:
            # getting data
            day_pg = [1,2,3,4,5,6,0]
            day_week = dt.strptime(date_,"%Y-%m-%d")
            hours,count_ = self.query.open_regression(dbConnection=dbConnection, mcc=mcc,day_week=day_pg[day_week.weekday()], type_=type_)

            if not hours or not count_:
                return {"error":True, "msg":"was not found data", "data":[]}
            # data 
            # model_ = numpy.poly1d(numpy.polyfit(hours, count_, 3))

            # # predict speed
            data=[]
            best_hour={"hour":0, "count":0}
            # for hour in range(0,23):
            #     predict = model_(hour)
            #     payload = _schemas.dashboard_regresion(
            #         hour=hour,
            #         count=predict,
            #         type_=type_)

            #     # get the best
            #     print(predict)
            #     if predict > best_hour["count"]:
            #         best_hour["count"] = int(predict)
            #         best_hour["hour"]=hour
            #         print(best_hour)

            #     data.append(payload)

            poly = PolynomialFeatures(degree=8, include_bias=False)
            x = numpy.array(hours)
            poly_features = poly.fit_transform(x.reshape(-1, 1))

            poly_reg_model = LinearRegression()
            poly_reg_model.fit(poly_features, count_)
            y_predicted = poly_reg_model.predict(poly_features)
            print(y_predicted)
            for key,preicted in enumerate(y_predicted):
                payload = _schemas.dashboard_regresion(
                    hour=hours[key],
                    count=preicted,
                    type_=type_
                )

                if preicted > best_hour["count"]:
                    best_hour["count"] = int(preicted)
                    best_hour["hour"]=hours[key]

                data.append(payload)

            return {
                "error":False,
                "msg":"Response Ok",
                "data":data,
                "bestHour":best_hour["hour"],
                "bestCount":best_hour["count"]
            }
        except Exception as err:
            print (err)
            return {"error":True, "msg":err.args[0], "data":[]}


class query:
    def __init__(self) -> None:
        pass

    def brands(self,dbConnection):
        try:
            with dbConnection as conn:
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

    def countries(self,dbConnection):
        try:
            with dbConnection as conn:
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

    def template(self,dbConnection):
        try:

            with dbConnection as conn:
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

    def device_response(self,dbConnection):
        try:

            with dbConnection as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT id, name FROM cota_device_responses_status_catalog
                        """
                    )
                    responses = cursor.fetchall()

            data=[Catalogs(id=response.id, name=response.name) for response in responses]
            error = False
            msg = ""

            return Response(
                msg=msg,
                error=error,
                data=data
            )
            
        except Exception as e:
            error = True
            msg = e.__str__()
            data = []

    def open_regression(self,dbConnection, mcc:str, day_week:int, type_:str ):
        try:

            with dbConnection as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        sql.SQL("""
                        WITH campaign as (
                                SELECT ID
                                FROM update u
                                WHERE u.startdate::date > (current_date - interval '90 days') and
                                extract(dow from u.startdate::date) = %(day_)s
                                and  u.mcc=%(mcc)s
                        )
                        SELECT to_char(DATE,'HH24') as hours, count(i.id) as count_
                                FROM campaign c  inner join IMEIS i  on (i.id=c.id)
                                WHERE {filter_status} AND i.DATE::date > (current_date - interval '90 days')
                                group by to_char(DATE,'HH24')
                                order by to_char(DATE,'HH24')
                        """).format(
                            filter_status=sql.SQL("STATUS is not null" if type_=="delivery" else "STATUS IN (2,36,37,38,39,50,51,52)")
                        ),
                        {
                            "mcc": mcc,
                            "day_": day_week,
                        }
                    )
                    opened = cursor.fetchall()
            hours=[int(tmp.hours) for tmp in opened]
            count_=[tmp.count_ for tmp in opened]
           
        except Exception as e:
            print(e.__str__())


        return hours,count_