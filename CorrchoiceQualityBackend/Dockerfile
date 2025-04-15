# Operating System
FROM python:3.11-alpine AS build-stage 

# Author 
LABEL maintainer="Kennedy Technologies, LLC"

# Arguments
ARG DEBIAN_FRONTEND=noninteractive aptitude install -q -y
ARG REQUIREMENT_FILE=requirements/prod.txt

ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements/ requirements/

RUN apk add --no-cache \
 	gcc \	
 	musl-dev \
 	libffi-dev \
 	openssl-dev \
 	mariadb-connector-c-dev \
 	build-base \
 	curl

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python get-pip.py
RUN pip install --upgrade pip
RUN pip install -r $REQUIREMENT_FILE
RUN rm get-pip.py


# Final stage (production)
FROM python:3.11-alpine

# Environment Variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Get this by echoing the sys.path and concatenating each item, then appending your application directoires
ENV PYTHONPATH=/usr/local/lib/python311.zip:/usr/local/lib/python3.11:/usr/local/lib/python3.11/lib-dynload:/usr/local/lib/python3.11/site-packages:/app:/app/shared

RUN apk add --no-cache mariadb-connector-c-dev bash

# Python packages
COPY --from=build-stage /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# System packages
COPY --from=build-stage /usr/local/lib /usr/local/lib

# Assign primary directory
WORKDIR /app

# Copy over project code into Docker filesystem
COPY . .

# Open Docker port 8000
EXPOSE 8000

#CMD python manage.py makemigrations && python manage.py migrate && python manage.py loaddata barebones && python manage.py runserver 0.0.0.0:8000
CMD python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000
