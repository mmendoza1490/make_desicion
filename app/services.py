from dataclasses import dataclass
import os
from datetime import datetime as dt
import csv

import sqlalchemy.orm as _orm
from sqlalchemy import and_, text
from psycopg2 import connect, extras, sql
import numpy
from sklearn.metrics import r2_score
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from .database import Database as _database
from .models import DecisionTree, LineaRegression
from .schemas import Schemas as _schemas
from app.types import Response, Catalogs, DecisionTreeData, DecisionTreeResponse

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

    def get_result_tree(self, dbConnection, session, brand, country, date_time, template):
    
        data = self.query.train_decision_tree_model(
            dbConnection,
            session, 
            brand=brand, 
            country=country, 
            date_time=date_time,
            template=template,
        )

        return data

    def get_result_regresion(self, dbConnection, type_, date_, mcc):
        try:
            # getting data
            day_pg = [1,2,3,4,5,6,0]
            day_week = dt.strptime(date_,"%Y-%m-%d")
            hours,count_ = self.query.open_regression(
                dbConnection=dbConnection, 
                mcc=mcc, 
                day_week=day_pg[day_week.weekday()], 
                type_=type_
            )

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

    def open_regression(self, dbConnection, mcc:str, day_week:int, type_:str ):
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

    def train_decision_tree_model(self, dbConnection, session, brand, country, date_time, template):
        day_pg = [1,2,3,4,5,6,0]


        # delete previous data from decision tree table
        deletion_query = text("DELETE FROM decision_tree;")

        session.execute(deletion_query)

        dt_obj = dt.strptime(date_time, '%Y-%m-%dT%H:%M:%SZ')
        
        try:
            with dbConnection as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT DISTINCT androidid, COUNT(*) total FROM
                        (SELECT androidid FROM imeis limit 1000) as imeis
                        GROUP BY androidid
                        """
                    )

                    result = cursor.fetchall()

            page_size = 50
            done = False
            offset = 0

            with dbConnection as conn:
                with conn.cursor() as cursor:
                    while not done:
                        cursor.execute(
                            """
                            SELECT DISTINCT androidid 
                            FROM (SELECT androidid FROM imeis limit 1000) imeis 
                            LIMIT %s OFFSET %s
                            """, (page_size, offset)
                        )

                        # result = cursor.fetchall()

                        davices = numpy.array(cursor.fetchall())
                        
                        offset += page_size

                        if davices.size == 0:
                            done = True
                            continue

                        for device in numpy.nditer(davices):
                            cursor.execute(
                                """
                                SELECT
                                    EXTRACT(dow from startdate) day_of_week,
                                    EXTRACT(hour from startdate) hour_of_day,
                                    U.template_id,
                                    U.oem,
                                    U.mcc,
                                    I.status
                                FROM update U
                                    INNER JOIN imeis I ON (U.id=I.id)
                                    INNER JOIN cota_campaign_templates CCT ON CCT.id=U.template_id
                                WHERE I.androidid=%(androidid)s AND
                                    i.status IS NOT NULL;
                                """,
                                {
                                    "androidid": device.item()
                                }
                            )

                            result = cursor.fetchall()

                            if not result:
                                continue

                            df = pd.DataFrame(result)

                            features = ["day_of_week", "hour_of_day", "template_id", "oem", "mcc"]

                            X = df[features]
                            Y = df["status"]
                            
                            # predict with decision tree model
                            dtree = DecisionTreeClassifier()
                            dtree.fit(X, Y)

                            predict = dtree.predict(
                                [[day_pg[dt_obj.weekday()], dt_obj.hour, template, brand, country]]
                            )

                            # save decision tree prediction
                            decision_tree_result = DecisionTree(
                                androidid=device.item(),
                                decision=str(predict[0]),
                                date=date_time
                            )

                            session.add(decision_tree_result)

                            session.commit()       


            group_result_query = text(
                """
                SELECT 
                    CASE 
                        WHEN decision = 1 THEN 'no_action' 
                        WHEN decision = 3 THEN 'closed' 
                        WHEN decision = 4 THEN 'error' 
                        ELSE 'opened' 
                    END AS name, 
                    COUNT(*) total 
                FROM decision_tree 
                GROUP BY name;
                """
            )

            results = session.execute(group_result_query)

            data = []

            for result in results:
                data.append(DecisionTreeData.parse_obj(result))

            msg = ""
            error = False

        except Exception as e:
            print(e.__str__())
            error = True
            msg = e.__str__()
            data = []

        return DecisionTreeResponse(
            msg=msg,
            error=error,
            data=data
        )

    # def get_data_from_csv(file_path: str) -> Generator:
    #     with open(file=file_path, mode="rb") as file_like:
    #         yield file_like.read()


    def cleanup(csv_path):
        os.remove(csv_path)

    def create_csv(self, session, response_status):
        try:
            result = session.execute("SELECT * FROM decision_tree;")

            # Open the CSV file for writing
            with open('static/responses_data.csv', 'w', newline='') as csvfile:
                # Create a CSV writer
                writer = csv.writer(csvfile)

                # Write the column names to the CSV file
                writer.writerow([column for column in result.keys()])

                # Write the rows to the CSV file
                writer.writerows(result.fetchall())

            session.close()

            return FileResponse(
                path='static/responses_data.csv',
                media_type="application/octet-stream",
                status_code=200,
                filename="responses_data.csv",
                # background=BackgroundTask(os.remove("static/responses_data.csv"))
            )

        except Exception as e:
            print(e.__str__())


        finally:
            os.remove("static/responses_data.csv")
            pass


