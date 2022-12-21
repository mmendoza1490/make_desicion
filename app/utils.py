import os
from typing import Generator


def get_data_from_csv(file_path: str) -> Generator:
    with open(file=file_path, mode="rb") as file_like:
        yield file_like.read()


def cleanup(csv_path):
    os.remove(csv_path)