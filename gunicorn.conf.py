import multiprocessing
import os

import dotenv

dotenv.load_dotenv()

syslog = True
dev = os.getenv("ENVIRONMENT") == "development"
port = os.getenv("FAST_API_PORT", 5000)
address = os.getenv("FAST_API_HOST")

reload = dev

bind = f"{address}:{port}"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 0
