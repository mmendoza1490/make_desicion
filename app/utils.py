import os
from typing import Generator
import pytz
from dateutil import parser


def get_data_from_csv(file_path: str) -> Generator:
    with open(file=file_path, mode="rb") as file_like:
        yield file_like.read()


def cleanup(csv_path):
    os.remove(csv_path)


def get_datetime_by_timezone(mcc, date_time, dbConnection):
    with dbConnection as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT timezone FROM users_admin.countries WHERE mcc = %(mcc)s
                """,
                {"mcc": mcc}
            )

            result = cursor.fetchone()
    utc = pytz.utc
    incoming_timezone = pytz.timezone(result.timezone)
    localized_date_time = incoming_timezone.localize(parser.parse(date_time))
    new_date_time = localized_date_time.astimezone(utc)
    new_str_date_time = new_date_time.strftime("%Y-%m-%dT%H:%M")

    return new_str_date_time

