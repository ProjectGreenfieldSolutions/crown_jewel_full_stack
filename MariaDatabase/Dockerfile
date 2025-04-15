# OS
FROM mariadb:11.3.2-jammy

LABEL maintainer="Kennedy Technologies, LLC"

# Installation
#RUN apt update -y && apt upgrade -y && apt install -y vim

WORKDIR /app

COPY . .

RUN chmod u+x *.sh

# Expose the MariaDB port
EXPOSE 3306