#!/bin/bash
###################################################################################
# Purpose:
# # Grab the latest backup file
# # Run restore command on remote container in shared volume
###################################################################################

# Variables
###################################################################################
CONTAINER_NAME="mariadb_container"
DATABASE_DIR="/app/backups/"
LOCAL_DIR="/scripts/backups/"
RETRIES=0
MAX_RETRIES=10
RETRY_DELAY=5
###################################################################################

# Functions
###################################################################################
# Restore the backup
restore_from_backup() {
  docker exec -i "${CONTAINER_NAME}" mariadb -u "${MYSQL_USER}" -p"${MYSQL_PASSWORD}" "${MYSQL_DATABASE}" < "${LOCAL_DIR}${LATEST_BACKUP_FILENAME}"
}
###################################################################################

# Find the latest backup file in the container
LATEST_BACKUP=$(docker exec "${CONTAINER_NAME}" sh -c "ls -t ${DATABASE_DIR}*.sql 2>/dev/null | head -n 1")

# Check if a backup was found
if [ -z "${LATEST_BACKUP}" ]; then
    echo "No backup files found in ${DATABASE_DIR}"
    exit 1
fi

# Grab only the filename
LATEST_BACKUP_FILENAME=$(basename "${LATEST_BACKUP}")
echo "Restoring from the latest backup: ${LATEST_BACKUP_FILENAME}"

# Attempt to restore from backup
while [ ${RETRIES} -lt ${MAX_RETRIES} ]; do
  RESULTS=$(restore_from_backup)
  if [ $? -eq 0 ]; then
    # Success message
    echo "Restoration completed."
    exit 0
  elif echo "${RESULTS}" | fgrep "connect to local server through socket"; then
    # Known error
    echo "ERROR: ${RESULTS}"
    RETRIES=$((RETRIES + 1))
    echo "Retrying in ${RETRY_DELAY} seconds..."
    sleep ${RETRY_DELAY}
  else
    # Catch all error
    echo "ERROR: ${RESULTS}"
    RETRIES=$((RETRIES + 1))
    echo "Retrying in ${RETRY_DELAY} seconds..."
    sleep ${RETRY_DELAY}
  fi
done

echo "Maximum amount of retries met ${MAX_RETRIES}."
exit 1