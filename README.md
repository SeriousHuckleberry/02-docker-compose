# Project 2 - Docker Compose: Flask + PostgreSQL

## 📌 Overview

This is **Project 2** in my DevOps learning series.

In this project, I am learning how to use **Docker Compose** to run and operate a multi-container application.

The application consists of:

- 🐍 Flask web application
- 🐘 PostgreSQL database
- 🐳 Docker
- 🐙 Docker Compose
- 🌐 Docker networking and service discovery
- 💾 Persistent Docker volumes
- 🔐 Environment variables and `.env`
- ❤️ PostgreSQL healthchecks
- 🔄 Container restart policies
- 🛠️ Docker Compose troubleshooting
- 📝 Git & GitHub

The main goal of this project is to understand how Docker Compose manages multiple containers, how those containers communicate, how configuration is injected, and how common operational problems are diagnosed.

> **Project scope:** Flask and PostgreSQL are used as workloads to demonstrate Docker Compose and DevOps concepts. This project is not intended to become a Flask application-development or CRUD project.

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

### Request / communication flow

```text
Browser
   |
   | http://localhost:5000
   ▼
Flask Container
   |
   | host = postgres
   | port = 5432
   ▼
Docker Compose DNS
   |
   ▼
PostgreSQL Container
```

---

# 📁 Project Structure

```text
02-docker-compose/
│
├── .dockerignore
├── .gitignore
├── .env                  # Local environment variables - NOT committed
├── .env.example          # Safe configuration template
├── Dockerfile
├── compose.yaml
├── app.py
├── requirements.txt
├── README.md
│
└── screenshots/
```

> The real `.env` file is intentionally ignored by Git. `.env.example` documents the variables required to run the project without exposing local credentials.

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
    restart: unless-stopped
    ports:
      - "5000:5000"
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    depends_on:
      postgres:
        condition: service_healthy

  postgres:
    image: postgres:16
    restart: unless-stopped
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 5s
      timeout: 5s
      retries: 5
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  postgres-data:
```

This configuration demonstrates the core Docker Compose concepts covered by this project:

- Multiple services in one Compose application
- Custom image build with `build:`
- Official image usage with `image:`
- Host-to-container port mapping
- Environment variable injection
- Service dependencies
- Healthchecks
- Restart policies
- Named volumes

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

The Flask service also uses:

```yaml
restart: unless-stopped
```

which configures Docker to restart the container after an unexpected exit, while respecting an intentional stopped state.

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

PostgreSQL also uses a healthcheck and restart policy.

---

# 🌐 Docker Networking

Docker Compose automatically creates a default application network:

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
    172.21.x.x           172.21.x.x
```

The Flask container can reach PostgreSQL using the service name:

```text
postgres:5432
```

instead of using the PostgreSQL container IP address.

This is important because container IP addresses can change when containers are recreated.

Docker's internal DNS resolves:

```text
postgres
```

to the current PostgreSQL container IP.

### Verify service discovery

```powershell
docker compose exec flask getent hosts postgres
```

This demonstrates that Compose's internal DNS can resolve the PostgreSQL service name.

---

# 🔗 Flask → PostgreSQL Connection

The Flask application uses the `psycopg` Python package to connect to PostgreSQL.

The connection uses:

```text
Host: postgres
Port: 5432
Database: provided through environment variables
User: provided through environment variables
Password: provided through environment variables
```

The application provides a `/db` endpoint to test the database connection and execute a PostgreSQL query.

Test it using:

```powershell
curl http://localhost:5000/db
```

Expected result will contain a successful connection message and the PostgreSQL version.

---

# 🔐 Environment Variables

Database configuration is stored in a local `.env` file.

Example local values:

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

A safe template is committed as `.env.example`:

```env
POSTGRES_DB=flaskdb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=*change-me*
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

> ⚠️ `.env` is useful for keeping configuration and credentials out of source code and Git, but it is not a secure production secret vault.

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

This demonstrated that PostgreSQL data is stored in the Docker volume rather than being dependent on the lifecycle of the container.

> ⚠️ Avoid `docker compose down -v` when you want to keep the database data because `-v` removes the Compose-managed volumes.

---

# ❤️ PostgreSQL Healthcheck

PostgreSQL uses a healthcheck based on `pg_isready`:

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
  interval: 5s
  timeout: 5s
  retries: 5
```

The purpose of the healthcheck is to verify that PostgreSQL is ready to accept connections.

Flask depends on PostgreSQL becoming healthy:

```yaml
depends_on:
  postgres:
    condition: service_healthy
```

This is different from simply starting PostgreSQL first. The dependency condition waits for PostgreSQL to report a healthy state.

Check the health status:

```powershell
docker compose ps
```

Expected PostgreSQL state:

```text
Up (healthy)
```

---

# 🔄 Restart Policy

Both services use:

```yaml
restart: unless-stopped
```

This configures Docker to automatically restart a container after an unexpected exit while still allowing an intentionally stopped container to remain stopped.

The restart policy can be inspected with:

```powershell
docker inspect 02-docker-compose-flask-1 --format "{{json .HostConfig.RestartPolicy}}"
```

Expected configuration includes:

```text
"Name":"unless-stopped"
```

The important DevOps concept is that restart policy is an **operational container setting**; it does not replace application health monitoring or orchestration systems used in larger production environments.

---

# 🧰 Container Operations and Troubleshooting

Docker Compose provides several commands used during day-to-day operations:

```powershell
docker compose ps
docker compose ps -a
docker compose logs --tail=30
docker compose exec flask sh
docker compose config
```

## Port conflict troubleshooting

A port conflict was intentionally reproduced during this project.

The Flask service requires host port `5000`:

```yaml
ports:
  - "5000:5000"
```

If another container is already using host port `5000`, Flask cannot bind to that port.

The troubleshooting workflow is:

```text
Compose start fails
       ↓
Check docker compose output
       ↓
Check running containers
       ↓
Identify the container using port 5000
       ↓
Remove the conflicting container
       ↓
Start Compose again
```

Useful commands:

```powershell
docker ps
docker port <container-name>
docker rm -f <container-name>
docker compose up -d
```

This exercise demonstrates a common Docker operational problem: **host port allocation conflicts**.

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

Use `.env.example` as the template.

For example:

```powershell
Copy-Item .env.example .env
```

Then update `.env` with your local values.

Do not commit the real `.env` file to Git.

## 4. Validate the Compose configuration

```bash
docker compose config
```

## 5. Build and start the containers

```bash
docker compose up -d --build
```

## 6. Check running containers

```bash
docker compose ps
```

Expected services:

```text
flask
postgres
```

PostgreSQL should report `healthy`.

## 7. Test Flask

Open:

```text
http://localhost:5000
```

Or use:

```bash
curl http://localhost:5000
```

## 8. Test PostgreSQL connection

```bash
curl http://localhost:5000/db
```

The endpoint should return a successful PostgreSQL connection message and version information.

---

# 🔍 Useful Docker Commands

### Validate Compose configuration

```bash
docker compose config
```

### Build the Flask image

```bash
docker compose build
```

### Start the services

```bash
docker compose up -d
```

### Start and rebuild

```bash
docker compose up -d --build
```

### View Compose services

```bash
docker compose ps
```

### View all containers, including stopped ones

```bash
docker compose ps -a
```

### View container logs

```bash
docker compose logs
```

### View the last 30 log lines

```bash
docker compose logs --tail=30
```

### View Flask logs

```bash
docker compose logs flask
```

### View PostgreSQL logs

```bash
docker compose logs postgres
```

### Execute a command in Flask

```bash
docker compose exec flask sh
```

### Execute PostgreSQL client

```bash
docker compose exec postgres psql -U postgres -d flaskdb
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

### Stop the services

```bash
docker compose stop
```

### Start stopped services

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
- [x] How Compose builds a custom image
- [x] How to use an official PostgreSQL image
- [x] How Compose creates a network
- [x] How containers communicate
- [x] Docker service-name DNS / service discovery
- [x] Flask container communicating with PostgreSQL
- [x] Docker volumes
- [x] Environment variables
- [x] `.env` files
- [x] Protecting `.env` from Git
- [x] `.env.example` configuration templates
- [x] `depends_on`
- [x] PostgreSQL healthchecks
- [x] Named volume persistence
- [x] Container lifecycle commands
- [x] Container logs and `docker compose exec`
- [x] Restart policies
- [x] Docker Compose configuration validation
- [x] Troubleshooting host port conflicts

---

# 📸 Screenshots

Screenshots will document the important DevOps concepts demonstrated in this project.

Recommended evidence:

```text
screenshots/
├── 01-compose-config.png
├── 02-running-services.png
├── 03-flask-app.png
├── 04-database-connectivity.png
├── 05-compose-network.png
├── 06-compose-logs.png
└── 07-port-conflict.png
```

### Suggested evidence

| Screenshot | Demonstrates |
|---|---|
| `01-compose-config.png` | Validated Compose configuration |
| `02-running-services.png` | Flask + PostgreSQL running and PostgreSQL healthy |
| `03-flask-app.png` | Flask service accessible on port 5000 |
| `04-database-connectivity.png` | Flask → PostgreSQL connectivity |
| `05-compose-network.png` | Docker Compose service discovery / DNS |
| `06-compose-logs.png` | Container logging and operational visibility |
| `07-port-conflict.png` | Troubleshooting a host port conflict |

Only include screenshots that have actually been captured.

---

# 🎯 Project Goal

The goal of this project is to understand how a multi-container application can be structured, configured, operated, and troubleshot using Docker Compose.

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
Networking / Service Discovery
     ↓
Environment Configuration
     ↓
Healthchecks
     ↓
Persistent Storage
     ↓
Restart Policies
     ↓
Operational Troubleshooting
```

This project is part of my **DevOps hands-on learning series**.

## ✅ Project Status

**Project 2 - Docker Compose: In final documentation stage**

Technical Docker Compose work is complete. The remaining task is to capture the final screenshots and perform the final README/Git review before moving to Project 3.
