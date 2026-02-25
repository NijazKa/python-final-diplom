FROM python:3.14-alpine3.21

WORKDIR /usr/src/app

COPY requirements.txt .
# install dependencies
# RUN pip install --upgrade pip
RUN pip install redis
RUN pip install --no-cache-dir -r requirements.txt

