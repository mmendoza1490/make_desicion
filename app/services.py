from dataclasses import dataclass
import os
from datetime import datetime as dt
import csv
from typing import Generator
import zipfile

from sqlalchemy import text
from psycopg2 import connect, extras, sql
import numpy
from sklearn.metrics import r2_score
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask

from .database import Database as _database
from .models import DecisionTree
from .schemas import Schemas as _schemas
from app.types import Response, Catalogs, DecisionTreeData, DecisionTreeResponse
from app.utils import cleanup, get_data_from_csv, get_datetime_by_timezone

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

    def get_result_tree(self, dbConnection, session, brand, country, date_time, template, universe):

        localized_date_time = get_datetime_by_timezone(country, date_time, dbConnection)
    
        data = self.query.train_decision_tree_model(
            dbConnection,
            session, 
            brand=brand, 
            country=country, 
            date_time=date_time,
            template=template,
            universe=universe
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
                return {"error":False, "msg":"no data was found", "data":[]}

            # # predict speed
            data=[]
            best_hour={"hour":0, "count":0}

            poly = PolynomialFeatures(degree=2, include_bias=False)
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
                                FROM campaign c  inner join imeis i  on (i.id=c.id)
                                WHERE {filter_status} AND i.DATE::date > (current_date - interval '90 days')
                                group by to_char(DATE,'HH24')
                                order by to_char(DATE,'HH24')
                        """).format(
                            filter_status=sql.SQL("STATUS is not null") if type_=="delivery" else sql.SQL("STATUS IN (2,36,37,38,39,50,51,52)")
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

    def train_decision_tree_model(self, dbConnection, session, brand, country, date_time, template, universe=1000):
        day_pg = [1,2,3,4,5,6,0]


        # delete previous data from decision tree table
        deletion_query = text("DELETE FROM decision_tree;")

        session.execute(deletion_query)

        dt_obj = dt.strptime(date_time, '%Y-%m-%dT%H:%M')
        
        try:

            page_size = int(os.getenv("PAGINATION_CHUNK_SIZE"))
            done = False
            offset = 0

            with dbConnection as conn:
                with conn.cursor() as cursor:
                    while not done and offset < universe:

                        cursor.execute(
                            """
                            WITH devices AS (
                            SELECT DISTINCT androidid
                            FROM (SELECT androidid FROM imeis LIMIT %s) imeis
                            LIMIT %s OFFSET %s                        
                            )
                            SELECT
                                EXTRACT(dow from startdate) day_of_week,
                                EXTRACT(hour from startdate) hour_of_day,
                                U.template_id,
                                U.oem,
                                U.mcc,
                                I.status,
                                I.androidid
                            FROM update U
                                INNER JOIN imeis I ON (U.id=I.id)
                                INNER JOIN cota_campaign_templates CCT ON CCT.id=U.template_id
                                INNER JOIN devices D ON D.androidid = I.androidid
                            WHERE I.status IS NOT NULL
                            """,(universe, page_size, offset)
                        )

                        result = cursor.fetchall()

                        if not result:
                            done = True
                            continue

                        df = pd.DataFrame(result)

                        imeis = set(df["androidid"])

                        features = ["day_of_week", "hour_of_day", "template_id", "oem", "mcc"]

                        for imei in imeis:

                            imei_exist = session.execute(
                                "SELECT androidid FROM decision_tree WHERE androidid = :value",
                                {"value": imei}
                            )

                            if imei_exist.fetchone():
                                continue

                            device_responses = df.loc[df["androidid"] == imei]

                            X = device_responses[features]
                            Y = device_responses["status"]
                            
                            # predict with decision tree model
                            dtree = DecisionTreeClassifier()
                            dtree.fit(X.values, Y)

                            predict = dtree.predict(
                                [[day_pg[dt_obj.weekday()], dt_obj.hour, template, brand, country]]
                            )

                            # save decision tree prediction
                            decision_tree_result = DecisionTree(
                                androidid=imei,
                                decision=str(predict[0]),
                                date=date_time
                            )

                            session.add(decision_tree_result)

                            session.commit()       

                        offset += page_size

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

    def create_csv(self, session, response_name):

        query = {
            "no_action": (
                "SELECT androidid FROM decision_tree WHERE decision = 1;"
            ),
            "closed": (
                "SELECT androidid FROM decision_tree WHERE decision = 3;"
            ),
            "error": (
                "SELECT androidid FROM decision_tree WHERE decision = 4;"
            ),
            "opened": (
                "SELECT androidid FROM decision_tree WHERE decision NOT IN (1, 3, 4);"
            )
        }

        try:
            result = session.execute(
                query.get(response_name)
            )

            path = os.getcwd() + "/static/"

            filename = response_name + "_responses"

            csv_file = filename + ".csv"

            zip_file = filename + ".zip"

            # Open the CSV file for writing
            with open(path + csv_file, 'w', newline='') as csvfile:
                # Create a CSV writer
                writer = csv.writer(csvfile)

                # Write the column names to the CSV file
                writer.writerow([column for column in result.keys()])

                # Write the rows to the CSV file
                writer.writerows(result.fetchall())

            session.close()

            with zipfile.ZipFile(path + zip_file, "w", zipfile.ZIP_DEFLATED) as zip:
                # Add the file to the ZIP archive with a new name
                zip.write(path + csv_file, csv_file)

                os.remove(path + csv_file)

            return StreamingResponse(
                content=get_data_from_csv(path + zip_file),
                media_type="application/octet-stream",
                status_code=200,
                headers={"Content-Disposition": "attachment; filename=" + zip_file},
                background=BackgroundTask(cleanup, path + zip_file)
            )

        except Exception as e:
            print(e.__str__())
