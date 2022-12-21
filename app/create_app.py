from contextlib import nullcontext
import os
from typing import Optional, List, Any

from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse, FileResponse
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

from app.types import Response, DecisionTreeResponse

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
        response_model=DecisionTreeResponse
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
        return data

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

    @app.get("/download-csv/{response_status}")
    def csv_data(
        response_status: str,
        session: _orm.Session = Depends(db.get_db),
    ):
        return queries.create_csv(session=session, response_status=response_status)

    return app