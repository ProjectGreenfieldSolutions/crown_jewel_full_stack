#!/bin/bash

# TODO - maybe include this, but will have to deal with git config user/pass creditionals
#git fetch;
#git pull;
ENV_STAGE="-f ./compose.dev.yaml"

## Check if Docker is running
#if ! systemctl is-active --quiet docker; then
#    echo "Docker is not running. Starting Docker..."
#    sudo systemctl start docker
#
#    # Check if Docker started successfully
#    if systemctl is-active --quiet docker; then
#        echo "Docker started successfully."
#    else
#        echo "Failed to start Docker. Please check the logs."
#        exit 1
#    fi
#else
#    echo "Docker is already running."
#fi

docker-compose ${ENV_STAGE} down ;
docker volume prune -f ;
docker-compose ${ENV_STAGE} build ;
docker system prune -f ;
docker-compose ${ENV_STAGE} up -d ;
