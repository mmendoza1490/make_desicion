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
6. [User Manual](#user-manual)


- **just for test**
7. [Requirements](#requirements)
8. [Running](#running-test)

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
# api init
FAST_API_HOST="0.0.0.0"
FAST_API_PORT="8800"
ENVIRONMENT="development"

# data base
HOST_DB="10.10.15.6"
PSQL_DB="cota"
USER_DB="user1"
PASS_DB="passwd1"
PORT_DB=5432

# chunk size that your PC can support
PAGINATION_CHUNK_SIZE=1000
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

# User Manual
[PDF1](static/mbd_user_manual.pdf)

# Just to test

## requirements

### Install Docker and docker-compose
* check this post  https://docs.docker.com/engine/install/ubuntu/

### if you have a firewall active
> Open port with firewall-cmd
``` bash
sudo firewall-cmd --add-port=8800/tcp --permanent
sudo firewall-cmd --reload
```
> Open port with ufw
``` bash
sudo ufw allow 8800
```
## running test

> Creating env file:
``` bash
cd make_desicion
cp .env-sample .env
```

> Updating var to connect data base:
``` bash
HOST_DB="172.10.11.1"
PSQL_DB="cota"
USER_DB="user1"
PASS_DB="passwd1"
PORT_DB=5432

# chunk size that your PC can support
PAGINATION_CHUNK_SIZE = 1000
```

> Running docker
``` bash
docker-compose -f docker-compose.yml up
```
> Docker will start the API at http://localhost:8800