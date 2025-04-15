#!/bin/bash

RED="\e[31m";
GREEN="\e[32m";
YELLOW="\e[1;33m";
END_COLOR="\e[0m";

# Script setup variables
BACKUP_DIR="backups";

# Ensure backup directory exists
if test ! -d "${BACKUP_DIR}"; then
  echo -e "${YELLOW}Back up folder doesn't exist${END_COLOR}";
  mkdir ${BACKUP_DIR};
fi

LATEST_BACKUP_FILE=`find ${BACKUP_DIR} -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -f2- -d" "`

if test -f "${LATEST_BACKUP_FILE}"; then
  echo -e "${YELLOW}Latest backup file found: ${LATEST_BACKUP_FILE}${END_COLOR}";
  echo -e "${YELLOW}Attempting to load the backup file${END_COLOR}";
  mariadb -u "${MSQL_USER}" -p"${MYSQL_ROOT_PASSWORD}" ${MYSQL_DATABASE} < ${LATEST_BACKUP_FILE};
  echo -e "${GREEN}Loaded the backup file ${LATEST_BACKUP_FILE}${END_COLOR}";
  exit 0;
fi

echo -e "${RED}Latest backup file doesn't exist!${END_COLOR}"
exit 1;

