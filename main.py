import os
import multiprocessing
from fastapi.staticfiles import StaticFiles

from dotenv import load_dotenv
import uvicorn
from app.create_app import create_app, debug

load_dotenv(override=True)

app = create_app()
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host=os.getenv("FAST_API_HOST"),
        port=int(os.getenv("FAST_API_PORT")),
        reload=debug,
        workers=2 * multiprocessing.cpu_count() + 1,
    )
