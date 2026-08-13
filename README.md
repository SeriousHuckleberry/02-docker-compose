# Project 2 - Docker Compose: Flask + PostgreSQL

## 📌 Overview

This is **Project 2** in my DevOps learning series.

In this project, I am learning how to use **Docker Compose** to run a multi-container application.

The application consists of:

- 🐍 Flask web application
- 🐘 PostgreSQL database
- 🐳 Docker
- 🐳 Docker Compose
- 🌐 Docker networking
- 💾 Persistent Docker volumes
- 🔐 Environment variables
- 📝 Git & GitHub

The main goal of this project is to understand how multiple Docker containers communicate with each other and how Docker Compose makes managing them easier.

---

# 🏗️ Project Architecture

```text
                         Docker Compose
                              |
                +-------------+-------------+
                |                           |
                ▼                           ▼
          Flask Container             PostgreSQL Container
          Python 3.13                 PostgreSQL 16
                |                           |
                |                           |
                +------ Docker Network ------+
                           |
                    postgres:5432
                           |
                           ▼
                    postgres-data
                     Docker Volume
```

---

# 📁 Project Structure

```text
02-docker-compose/
│
├── .dockerignore
├── .gitignore
├── .env                  # Local environment variables - NOT committed
├── Dockerfile
├── compose.yaml
├── app.py
├── requirements.txt
├── README.md
│
└── screenshots/
```

---

# 🛠️ Technologies Used

- Python 3.13
- Flask
- PostgreSQL 16
- Docker
- Docker Compose
- Git
- GitHub
- VS Code

---

# 🐳 Dockerfile

The Flask application is built using the following Dockerfile:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

## What I Learned

### `FROM`

Provides the base image for the container.

```dockerfile
FROM python:3.13-slim
```

### `WORKDIR`

Sets the working directory inside the container.

```dockerfile
WORKDIR /app
```

### `COPY`

Copies files from the build context into the container.

```dockerfile
COPY requirements.txt .
COPY . .
```

### `RUN`

Runs a command while building the image.

```dockerfile
RUN pip install -r requirements.txt
```

### `EXPOSE`

Documents the port used by the application.

```dockerfile
EXPOSE 5000
```

### `CMD`

Specifies the command used to start the application.

```dockerfile
CMD ["python", "app.py"]
```

---

# 🐙 Docker Compose

Docker Compose is used to manage both the Flask and PostgreSQL containers.

The current `compose.yaml` contains two services:

```yaml
services:
  flask:
    build: .
    ports:
      - "5000:5000"
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

  postgres:
    image: postgres:16
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  postgres-data:
```

---

# 📦 Services

## Flask

The Flask service is built from the local Dockerfile.

```yaml
flask:
  build: .
```

Port `5000` is published:

```yaml
ports:
  - "5000:5000"
```

This allows the application to be accessed from the host machine:

```text
http://localhost:5000
```

---

## PostgreSQL

PostgreSQL runs using the official PostgreSQL 16 image:

```yaml
postgres:
  image: postgres:16
```

PostgreSQL uses port `5432` internally.

It does not need:

```yaml
ports:
  - "5432:5432"
```

because Flask and PostgreSQL communicate through the Docker Compose network.

---

# 🌐 Docker Networking

Docker Compose automatically created a network:

```text
02-docker-compose_default
```

Both containers are connected to this network.

Example:

```text
02-docker-compose_default
        |
        +-------------------+
        |                   |
        ▼                   ▼
     Flask              PostgreSQL
   172.21.0.3           172.21.0.2
```

The Flask container can reach PostgreSQL using the service name:

```text
postgres:5432
```

Instead of using the PostgreSQL container IP address.

This is important because container IP addresses can change when containers are recreated.

Docker's internal DNS resolves:

```text
postgres
```

to the current PostgreSQL container IP.

---

# 🔗 Flask → PostgreSQL Connection

The Flask application uses the `psycopg` Python package to connect to PostgreSQL.

The connection uses:

```text
Host: postgres
Port: 5432
Database: flaskdb
User: postgres
Password: provided through environment variables
```

The application provides a `/db` endpoint to test the database connection.

Test it using:

```bash
curl http://localhost:5000/db
```

Expected response:

```text
PostgreSQL connection successful!
```

---

# 🔐 Environment Variables

Database configuration is stored in a local `.env` file.

Example:

```env
POSTGRES_DB=flaskdb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

The `.env` file is **not committed to GitHub**.

It is added to `.gitignore`:

```gitignore
.env
```

Docker Compose reads the values from `.env` and passes them to the containers.

The flow is:

```text
.env
 |
 | POSTGRES_DB
 | POSTGRES_USER
 | POSTGRES_PASSWORD
 |
 ▼
Docker Compose
 |
 +-------------------+
 |                   |
 ▼                   ▼
Flask             PostgreSQL
Container          Container
```

> ⚠️ `.env` is useful for keeping configuration and credentials out of source code and Git, but it is not a secure secret vault.

---

# 💾 Persistent Docker Volume

PostgreSQL uses a named Docker volume:

```yaml
volumes:
  - postgres-data:/var/lib/postgresql/data
```

The volume is mounted inside the PostgreSQL container at:

```text
/var/lib/postgresql/data
```

The idea is:

```text
PostgreSQL Container
        |
        ▼
/var/lib/postgresql/data
        |
        ▼
postgres-data
Docker Volume
```

The purpose of the volume is to keep database data even if the PostgreSQL container is removed.

## Persistence Test

To verify that the PostgreSQL data survives container deletion:

1. Created a test table named `persistence_test`.
2. Inserted test data into the table.
3. Stopped the PostgreSQL container.
4. Removed the PostgreSQL container.
5. Confirmed that the Docker volume still existed.
6. Created a new PostgreSQL container using Docker Compose.
7. Queried the table again.

The data was still present after the new PostgreSQL container was created.

This demonstrated that the PostgreSQL data is stored in the Docker volume rather than being dependent on the lifecycle of the container.
---

# 🚀 Running the Project

## 1. Clone the repository

```bash
git clone <repository-url>
```

## 2. Enter the project directory

```bash
cd 02-docker-compose
```

## 3. Create the `.env` file

Create a file named:

```text
.env
```

Add:

```env
POSTGRES_DB=flaskdb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

Do not commit this file to Git.

---

## 4. Build the Flask image

```bash
docker compose build
```

---

## 5. Start the containers

```bash
docker compose up -d
```

---

## 6. Check running containers

```bash
docker compose ps
```

Expected services:

```text
flask
postgres
```

---

## 7. Test Flask

Open:

```text
http://localhost:5000
```

Or use:

```bash
curl http://localhost:5000
```

---

## 8. Test PostgreSQL connection

```bash
curl http://localhost:5000/db
```

Expected:

```text
PostgreSQL connection successful!
```

---

# 🔍 Useful Docker Commands

### List running containers

```bash
docker ps
```

### List Docker images

```bash
docker images
```

### List Docker volumes

```bash
docker volume ls
```

### List Docker networks

```bash
docker network ls
```

### Inspect the Compose network

```bash
docker network inspect 02-docker-compose_default
```

### View Compose services

```bash
docker compose ps
```

### View container logs

```bash
docker compose logs
```

### View Flask logs

```bash
docker compose logs flask
```

### View PostgreSQL logs

```bash
docker compose logs postgres
```

### Stop the services

```bash
docker compose stop
```

### Start the services again

```bash
docker compose start
```

### Remove containers and network

```bash
docker compose down
```

> ⚠️ Avoid `docker compose down -v` when you want to keep PostgreSQL data because it also removes the Compose-managed volumes.

---

# 🧠 What I Have Learned

- [x] What Docker Compose is
- [x] How to define multiple services
- [x] How Compose builds an image
- [x] How Compose creates a network
- [x] How containers communicate
- [x] Docker service-name DNS
- [x] Flask container communicating with PostgreSQL
- [x] PostgreSQL Docker image
- [x] Docker volumes
- [x] Environment variables
- [x] `.env` files
- [x] Protecting `.env` from Git
- [x] Basic Docker Compose commands

## Still To Learn

- [x] Test PostgreSQL data persistence
- [ ] Improve the Flask application
- [ ] Add database operations
- [ ] Improve security
- [ ] Add health checks
- [ ] Final project documentation

---

# 📸 Screenshots

Screenshots will be added as the project progresses.

Planned screenshots:

```text
screenshots/
├── docker-compose-build.png
├── docker-compose-ps.png
├── docker-network.png
├── flask-postgres-connection.png
├── docker-volume.png
└── database-persistence.png
```

---

# 🎯 Project Goal

The goal of this project is to understand how a real multi-container application can be structured using Docker Compose.

By the end of this project, I want to understand:

```text
Application
     ↓
Docker
     ↓
Docker Compose
     ↓
Multiple Containers
     ↓
Networking
     ↓
Database
     ↓
Persistent Storage
     ↓
Environment Configuration
```

This project is part of my **DevOps hands-on learning series**.