#!/bin/bash
###################################################################################
# Purpose:
# # Get the docker service up and running
# # Drop the currently running docker environment, if applicable
# # Clear the volumes (disk space) used to mount into the docker container
# # Rebuild the docker environment
# # Clear stale docker containers
# # Run the docker containers in headless mode
###################################################################################

# Target environment
ENV_STAGE="-f ./compose.prod.yaml"

# Check if Docker is running
if ! systemctl is-active --quiet docker; then
    echo "Docker is not running. Starting Docker..."
    sudo systemctl start docker

    # Check if Docker started successfully
    if systemctl is-active --quiet docker; then
        echo "Docker started successfully."
    else
        echo "Failed to start Docker. Please check the logs."
        exit 1
    fi
else
    echo "Docker is already running."
fi

# Spin down docker containers
docker compose ${ENV_STAGE} down ;

# Clear volumes on host
docker volume prune -f ;

# Rebuild the docker environment
docker compose ${ENV_STAGE} build ;

# Clear stale containers
docker system prune -f ;

# Spin up the docker containers in headless mode
docker compose ${ENV_STAGE} up -d ;
