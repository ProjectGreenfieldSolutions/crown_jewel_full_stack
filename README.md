# Technical Documentation

## Overview

This project utilizes Docker and Docker Compose to orchestrate the following containers:

- **Mariadb**: A relational database management system.
- **Django**: Backend service handling API and business logic.
- **NiceGUI**: Frontend user interface.
- **Script Runner**: Container for running generic scripts.

Each container communicates over a shared network (`quality-net`), and Docker Compose manages the services and their dependencies.

---

## Installation Steps
### Running Docker on Linux
* [Installing Docker on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
  * Commands executed
```bash
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

---

### Running Docker on Windows 
* Install on Windows
  * [Docker Desktop version 4.24.1](https://docs.docker.com/desktop/release-notes/#4241)
    * This version doesn't have the broken authentication that future version seem to have on Windows

---

## Basic Docker Compose Commands 
```bash
docker compose down ;    # Spins down running docker containers
docker volume prune -f ; # Deletes volumes used to persist container data from host machine
docker compose build ;   # Uses both the compose.yaml and Dockerfile(s) to construct the containers
docker system prune -f ; # Deletes any unused containers from the host machine
docker compose up -d ;   # Spins up the built containers in headless mode
```

---

# Project Specific Knowledge

---

## Application start-up / configuration settings
- `compose.prod.yaml` is the production version of the Docker Compose configuration
- `reboot_application.sh` is the production start-up script
  - This executes from cron upon reboot, on the live server
- `compose.dev.yaml` is the development version of the Docker Compose configuration
- `reboot_server_dev.sh` is the development start-up script
  - Needs to be ran from terminal
## File Hierarchy

---

### ScriptRunner
- **Folder Name**: `ScriptRunner`
- **Purpose**: The command and control container that has mounted volumes between the containers. It is responsible for managing administrative tasks that interact with other services/containers.
- **Primary Objectives**:
  - **Log File Management**: Regularly prunes old logs to maintain system performance and prevent storage overuse.
  - **Database Backup**: Periodically creates backups of the MariaDB database and stores them in a designated backup location or volume.
  - **Database Restore**: Handles restoring the database from backup files when required. The container can be triggered to restore the most recent backup or a specific backup file.
  
- **Volumes**:
  - `/var/log`: Mounts to a shared volume with other services to allow central log management.
  - `/scripts/backups`: A shared volume with the `mariadb` container to store backup files.
  
- **Commands**:
  - `backup_db.sh`: A script for backing up the MariaDB database.
    - Destination backup in `/scripts/backups` (ScriptRunner) or `/app/backups` (MariaDB)
  - `restore_db.sh`: A script for restoring the database from the **latest** backup.
  - `clear_logs.sh`: A script that prunes old log files from the `/var/log` directory, for each container.

---

### Django
- **Folder Name**: `CorrchoiceQualityBackend`
- **Purpose**: The backend service, built on the Django web framework, that manages the core application logic, APIs, and interactions with the database.
- **Primary Objectives**:
  - **API Management**: Exposes RESTful APIs to interact with the frontend and other services.
  - **Business Logic**: Handles all core business logic, processing data, and enforcing business rules.
  - **Database Interaction**: Manages interactions with the MariaDB database, including CRUD operations, migrations, and schema updates.
  
- **Structure**:
  - `settings.py`: Contains Django configurations, including database connections, security settings, and API configuration.
  - `urls.py`: Maps API routes to corresponding view functions and classes.
  - `models.py`: Defines the database models that are used to interact with the MariaDB database.

- **Commands**:
  - `python manage.py makemigrations`: Script to generate new schema, if models are updated.
  - `python manage.py migrate`: Script to use the new schema to create the column changes in database.

---

#### Purpose of `urls.py` in Django

In Django, the `urls.py` file is responsible for defining the URL patterns of the application and routing incoming HTTP requests to the appropriate views. It serves as the URL dispatcher for the application.

- How it was used in this project:
  - Endpoints for the front end to connect to
---

#### Purpose of `settings.py` in Django

The `settings.py` file contains all the configuration settings for a Django project, such as database settings, middleware, static files configurations, installed apps, and other global project settings that define the behavior and structure of the application.

- How it was used in this project:
  - Management of the Django configurations; database connections, debugging, application packages, timezone, secret key, allowed hosts
---

#### Purpose of `fixtures/` in Django

The `fixtures/` directory is used to store serialized data files in formats such as JSON, XML, or YAML. These fixtures can be loaded into the database to populate it with predefined data or used for testing purposes.

- How it was used in this project:
  - "Pre-warms" the application with bare minimum data so that the front end can function appropriately
---

#### Purpose of `management/` in Django

The `management/` directory contains custom Django management commands. These are Python scripts that extend the Django management command framework and are used to perform specific tasks from the command line, such as batch processing, data manipulation, or administration tasks.

- How it was used in this project:
  - Manually execution of code, that pulled in client provide CSVs and performed database CRUD operations to import the years worth of data.
  - Secondary, could be repurposed to cycle through that CSVs dataset and make update... But would be wise to just write something that loops through the database directly. Much faster.
---

#### Purpose of `migrations/` in Django

The `migrations/` directory contains migration files that define the changes to the database schema. These files allow Django to track and apply changes to the database structure, such as adding or modifying tables, fields, and relationships, ensuring the database is in sync with the models.

- How it was used in this project:
  - Not really used, but good to know about to see **when** things changed.
---

#### Purpose of `models/` in Django

The `models/` directory contains Python classes that define the structure of the database. These classes represent the data entities of the application and include the fields and behavior of the data. Django automatically generates the corresponding database tables from these models.

- How it was used in this project:
  - Literally everything database schema related is done here in. Inheritance made life super nice when building out these Models/Classes.
---

#### Purpose of `services/` in Django

The `services/` directory typically contains business logic or service layer code that acts as an intermediary between views and models. It is used to organize complex logic and keep views and models decoupled, promoting maintainability and reusability.

- How it was used in this project:
  - All Progress related queries reside in here
---

#### Purpose of `views/` in Django

The `views/` directory contains functions or classes that handle HTTP requests and return HTTP responses. Views are responsible for processing the request data, interacting with models, and returning data in response to the user’s request.

- How it was used in this project:
  - Issues JSON responses based on user's input.
---

### Mariadb
- **Folder Name**: `MariaDatabase`
- **Purpose**: The database service using MariaDB, responsible for storing all application data.
- **Primary Objectives**:
  - **Database Management**: Manages the storage, retrieval, and organization of application data.
  - **Data Integrity**: Ensures data integrity, enforcing schema rules and relationships.

- **Commands**:
  - **(Deprecated by ScriptRunner)** `restore_to_latest_backup.sh`: Original means for restoring the database 
  - `mariadb -uroot -p`: Command to access the mariadb terminal 
    - u = username
    - p = yes prompt for password
      - Password can be found in `production.env` or `development.env`
  - `CONNECT corrchoice_qc_dev;`: Connects to the database for this application.
  - `SHOW TABLES;`: Show all tables.
  - `SELECT * FROM api_litho;`: Show all columns/records from `api_litho` table.
  - `SELECT username FROM api_account;`: Show all usernames in the system.

---

### NiceGUI
- **Folder Name**: `NiceGuiFrontEnd`
- **Purpose**: The frontend service that uses NiceGUI to provide a graphical user interface (GUI) for users to interact with the system.
- **Primary Objectives**:
  - **User Interface**: Provides an intuitive, easy-to-use interface for interacting with the application, built with the NiceGUI library.
  - **User Interaction**: Allows users to interact with the Django backend via the frontend interface, such as submitting forms, viewing data, and running reports.
  - **Frontend Routing**: Handles the routing of frontend views and integrates them with backend APIs.

- **Structure**:
  - `main.py`: The main script that sets up and runs the NiceGUI app.
  - `core/App.py`: 
  - `core/QualityDashApp.py`: 
  - `components/`: Directory containing reusable GUI components (forms, tables, buttons).

---

