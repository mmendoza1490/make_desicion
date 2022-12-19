from contextlib import nullcontext
import os
from typing import Optional, List, Any

from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
import sqlalchemy.orm as _orm
from fastapi.responses import JSONResponse
from fastapi import  status
from fastapi.templating import Jinja2Templates

from .schemas import Schemas as _schemas
from .services import (
    Service,
    Data_base as db,
    query
)

from app.types import Response

from dotenv import load_dotenv

load_dotenv(override=True)

debug: bool = os.getenv("ENVIRONMENT") == "development"

queries = query()
services_ = Service()

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

    @app.get(
        "/tree/{brand}/{country}/{date_time}/{template}", 
        response_model=_schemas.tree_desicion
    )
    def verify_devices(
        brand: str,
        country: str,
        date_time: str,
        template: str,
        db:Any = Depends(db.connect),
        session: _orm.Session = Depends(db.get_db),
    ):
        data = services_.get_result_tree(
            dbConnection=db,
            session=session,
            brand=brand, 
            country=country, 
            date_time=date_time, 
            template=template
        )
        return None

    @app.get("/regression/{type_}/{mcc}/{date_}", response_model=dict())
    def linear_regression(
        type_:str,
        date_:str,
        mcc:str,
        db:Any = Depends(db.connect),
    ): 
        data = services_.get_result_regresion(dbConnection=db, type_=type_, date_=date_,mcc=mcc)
        return data

    @app.get("/brands", response_model=Response)
    def brands(
        db:Any = Depends(db.connect)
    ):
        return queries.brands(dbConnection=db)

    @app.get("/countries", response_model=Response)
    def countries(db:Any = Depends(db.connect)):
        return queries.countries(dbConnection=db)

    @app.get("/templates", response_model=Response)
    def template(db:Any = Depends(db.connect)):
        return queries.template(dbConnection=db)

    @app.get("/device-responses", response_model=Response)
    def campaign_responses(db:Any = Depends(db.connect)):
        return queries.device_response(dbConnection=db)

    return app