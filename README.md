# Make the Best Desicion
machine learning based tool - make the best desicion MBD


## Repository

[https://github.com/mmendoza1490/make_desicion.git](https://github.com/mmendoza1490/make_desicion.git)

## Table of Contents

- **to programmers**
1. [System Requirements](#system-requirements)
2. [Package Manager](#package-manager)
3. [Installation](#installation)
4. [enviroment](#enviroment)
5. [Running](#running)

- **just for test**
6. [Requirements](#requirements)
7. [Running](#running-test)

## System Requirements

- CPython >= 3.9 < 3.10

- Pip >= 21.1.1

- Git >= 2.31.1

## Package Manager

- Poetry >= 1.1.6

## Installation

```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -
echo 'export PATH="$HOME/.poetry/bin:$PATH"' >> $HOME/.bashrc
source $HOME/.bashrc

cd dir_project
poetry shell
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

## Running

### prerequisite command

```bash
cd make_desicion
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

# Just to test

## requirements

* Docker and docker-compose
``` bash
apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```
## running test

> Creating env file:
``` bash
cd make_desicion
cp .env-sample .env
```

> Updating var to connect data base:
``` bash
HOST_DB="10.10.15.6"
PSQL_DB="cota"
USER_DB="user1"
PASS_DB="passwd1"
PORT_DB=5432
```

> Running docker
``` bash
docker-compose -f docker-compose.yml up
```
> Docker will start the API at http://localhost:8001