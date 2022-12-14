from contextlib import nullcontext
import os
from typing import Optional, List

from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
import sqlalchemy.orm as _orm
from fastapi.responses import JSONResponse
from fastapi import  status
from fastapi.templating import Jinja2Templates

from .schemas import Schemas as _schemas
from .services import (
    Service as _services,
    Data_base as db,
    query
)

from app.types import Response

from dotenv import load_dotenv

load_dotenv(override=True)

debug: bool = os.getenv("ENVIRONMENT") == "development"

queries = query()

def create_app() -> FastAPI:

    app = FastAPI(debug=debug)
    templates = Jinja2Templates(directory="templates")

    db.create_database()

    app = FastAPI(
        docs_url="/help",
        title="Make the Best Desicion - MBD",
        description="Machine learning to make the best desicion",
        version="1.0.0",
        terms_of_service="https://digitalreef.com/",
        contact={
            "name": "DigitalReef",
            "url": "https://digitalreef.com/",
        },
    )

    @app.get("/", response_class=HTMLResponse)
    def home(
        request: Request,
    ):
        url=request.base_url
        return templates.TemplateResponse("home.html",context={
            "request": request, 
            "url":url,
        }, status_code=200)

    @app.get("/tree", response_model=_schemas.tree_desicion)
    def verify_devices(
        db: _orm.Session = Depends(db.get_db),
    ):
        return None

    @app.get("/regression/{_type}/{mcc}/{_date}", response_model=dict())
    def linear_regression(
        _type:str,
        _date:str,
        mcc:str,
        db: _orm.Session = Depends(db.get_db),
    ): 
        data = _services.get_result_regresion(_type=_type, _date=_date,mcc=mcc)
        return data

    @app.get("/brands", response_model=Response)
    def brands():
        return queries.brands(DbConnection=db.connect())

    @app.get("/countries", response_model=Response)
    def countries():
        return queries.countries(DbConnection=db.connect())

    @app.get("/templates", response_model=Response)
    def template():
        return queries.template(DbConnection=db.connect())

    return app