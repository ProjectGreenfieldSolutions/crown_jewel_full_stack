#!/bin/bash
###################################################################################
# Purpose: Run a remote database backup command to backup the environments database
###################################################################################

# Variables
########################################################################################
CONTAINER_NAME="mariadb_container"                      # Docker container name
BACKUP_DIR="/scripts/backups"                           # Target directory
DATE=$(date +"%Y%m%d_%H%M%S")                           # Get timestamp
BACKUP_FILE="${BACKUP_DIR}/mariadb_backup_${DATE}.sql"  # Create file name
DAYS_TO_KEEP=$((14 + 1))                                # Number of days to keep backups
########################################################################################

# Ensure the backup directory exists
mkdir -p $BACKUP_DIR;

# Run the backup command using docker exec
docker exec $CONTAINER_NAME mariadb-dump -u ${MYSQL_USER} -p"${MYSQL_PASSWORD}" ${MYSQL_DATABASE} > ${BACKUP_FILE};

# Optional: Clean up old backups (e.g., older than 14 days)
find $BACKUP_DIR -type f -name "*.sql" -mtime +${DAYS_TO_KEEP} -exec rm {} \;

# Success message
echo "Backup completed: ${BACKUP_FILE}";
