# Make the Best Desicion
machine learning based tool - make the best desicion MBD


## Repository

[https://github.com/mmendoza1490/make_desicion.git](https://github.com/mmendoza1490/make_desicion.git)

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Package Manager](#package-manager)
3. [Dependencies](#dependencies)
4. [Installation](#installation)
5. [enviroment](#enviroment)
6. [Running](#running)

## System Requirements

- CPython >= 3.9 < 3.10

- Pip >= 21.1.1

- Git >= 2.31.1

## Package Manager

- Poetry >= 1.1.6

## Dependencies

- python = "^3.9"
- fastapi = "^0.78.0"
- uvicorn = "^0.20.0"
- SQLAlchemy = "^1.4.39"
- sqlalchemy-orm = "^1.2.2"
- gunicorn = "^20.1.0"
- Jinja2 = "^3.1.2"
- pandas = "^1.5.2"
- scikit-learn = "^1.1.3"
- matplotlib = "^3.6.2"
- python-dotenv = "^0.21.0"
- psycopg2-binary = "^2.9.5"

## Installation

```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -
echo 'export PATH="$HOME/.poetry/bin:$PATH"' >> $HOME/.bashrc
source $HOME/.bashrc
poetry install
```
## enviroment

```bash
FAST_API_HOST="127.0.0.1"
FAST_API_PORT="5000"
ENVIRONMENT="development"

HOST_DB="10.10.20.15"
PSQL_DB="cota"
USER_DB="postgres"
PASS_DB="psql-1234"
PORT_DB="5432"
```

### Running

### prerequisite command

```bash
poetry shell
```

## Api

```bash
gunicorn  main:app
```

## Deployment

### An example of a linux-like service for production

```bash
[Unit]
Description=make the best desicion

[Service]
WorkingDirectory=/dir/make_desicion/
ExecStart=/dir/make_desicion/.venv/bin/gunicorn  main:app
Restart=always
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=mbd-logs
User= user01
Group= user01

[Install]
WantedBy=multi-user.target
```
