# Pipeline Airflow Project

This project sets up an Apache Airflow environment using Docker for data analysis Pipelines. It includes a PostgreSQL database, Redis as a message broker, and a web interface for managing workflows (DAGs).

[![Apache Airflow](https://img.shields.io/badge/Apache-Airflow-blue?logo=apache-airflow)](https://airflow.apache.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-blue?logo=postgresql)](https://www.postgresql.org/)

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Creating DAGs](#creating-dags)
- [License](#license)

## Features

- Runs Apache Airflow using the CeleryExecutor.
- Uses PostgreSQL as the backend database.
- Uses Redis as the message broker.
- Easily configurable using Docker Compose.

## Getting Started

To get started with this project, follow these steps:

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```
2. Create a .env file to store environment variables.
3. Build and start the services using Docker Compose:

   ```bash
   docker-compose up --build
   ```

This command will start the PostgreSQL, Redis, Airflow web server, and Airflow scheduler.

## Usage

After the services are running locally , you can access the Airflow web UI at http://localhost:8080. Use the following credentials to log in:

- **Username**: admin
- **Password**: admin

## Initialize the Database

If you need to initialize the database, you can do so by running the following command:

```bash
docker-compose run airflow-init
```

## Stop the Services

To stop the services, press Ctrl+C in the terminal where the Docker Compose is running or execute:

```bash
docker-compose down
```

## Creating DAGs

You can create your DAG files in the `dags` directory. Airflow will automatically detect and load them. Ensure that your DAG files follow the proper Python syntax and conventions.
