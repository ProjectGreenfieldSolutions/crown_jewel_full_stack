#!/bin/bash
###################################################################################
# Purpose:
# # Loop through containers on the network
# # Execute a shell command to remove log files older than target date
# # Note: /var/log is unique for each container
###################################################################################

# Variables
###################################################################################
DOCKER_NETWORK="quality_net" # Name of the network which this environment resides in
LOG_DIRECTORY="/var/log"     # Directory of which the logs are located
DAYS_TO_KEEP=$((7 + 1))      # Number of days to keep log files
###################################################################################

# Get the list of container IDs in the specified network
CONTAINERS=$(docker network inspect -f '{{range .Containers}}{{.Name}} {{end}}' "${DOCKER_NETWORK}")

# Loop through each container and remove old log files
for CONTAINER in ${CONTAINERS}; do
    echo "Cleaning up logs in container: $CONTAINER"
    docker exec "$CONTAINER" find "${LOG_DIRECTORY}" -type f -name "*.log" -mtime +${DAYS_TO_KEEP} -exec rm -f {} \;
done

# Success message
echo "Log cleanup completed."
