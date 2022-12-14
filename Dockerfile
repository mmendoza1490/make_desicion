FROM python:3.10.0 as python-base

LABEL version="1.0"
LABEL description="Machine learning digitalreef"

# Set var
ARG APP_NAME=make_desicion
ARG APP_PATH=/root/home/$APP_NAME
ARG PYTHON_VERSION=3.10.0

ENV C_FORCE_ROOT=1
ENV PROJECT_DIR=${APP_PATH}

RUN apt-get update
RUN pip3 install --upgrade pip
RUN apt-get install -y curl

# copy project
WORKDIR $PROJECT_DIR
COPY . .

# install dependency
RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 8800
WORKDIR $PROJECT_DIR
