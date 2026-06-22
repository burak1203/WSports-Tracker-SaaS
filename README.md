# WSports Tracker

A SaaS backend and staff management system built with FastAPI and Vue.js. It handles role-based access control (RBAC), commission tracking, and includes a full Docker + Nginx proxy setup with CI/CD automation.

## Overview

<p align="center">
  <img src="https://github.com/user-attachments/assets/4548dfba-263f-486b-a8db-655e700c5693" width="48%" alt="Dashboard UI" />
  <img src="https://github.com/user-attachments/assets/f5247dd1-9925-4606-a20f-e7392c0d93bb" width="48%" alt="Swagger UI" />
</p>

**Database**
<p align="center">
  <img src="https://github.com/user-attachments/assets/a7627e60-f781-4e5c-9e74-9f169fa67a8f" width="48%" alt="Database ER Diagram" />
</p>

## Features

* **Role-Based Access (RBAC):** Hierarchical authorization for different staff roles (Admin, Infocu, Kasa, Yuzdeci).
* **Soft-Delete Mechanism:** Staff accounts are deactivated rather than physically deleted to keep historical financial data and reports intact.
* **Dockerized Setup:** Full-stack containerization. Uses multi-stage builds for the frontend to keep the final image lightweight.
* **Nginx Reverse Proxy:** Routes traffic between the Vue.js frontend and FastAPI backend containers, avoiding CORS issues completely.
* **Automated CI/CD:** A GitHub Actions pipeline that verifies Python linters, Node.js builds, and tests the Docker compose build process on every push.

## Tech Stack

* **Backend:** Python, FastAPI, SQLAlchemy, PostgreSQL
* **Frontend:** Vue.js, Node.js
* **Infrastructure:** Docker, Docker Compose, Nginx, GitHub Actions

## Local Development

You don't need Python or Node.js installed locally. The entire stack runs via Docker.

## Demo Credentials

When the application is running, you can use the following default accounts to test different RBAC roles:

* **Admin Role:**
  * Username: `admin_yilmaz`
  * Password: `123456`
* **Infocu (Sales) Role:**
  * Username: `infocu_ali`
  * Password: `123456`

### 1. Clone the repository

```bash
git clone https://github.com/burak1203/WSports-Tracker-SaaS.git
cd WSports-Tracker-SaaS
```

### 2. Start the application

```bash
docker compose up -d --build
```

### 3. Access the services

* **Frontend UI:** http://localhost:8080
* **API Docs (Swagger):** http://localhost:8000/docs
* **Database Port:** 5433

## Security

Passwords are encrypted using bcrypt. Deactivated (soft-deleted) accounts are strictly validated and blocked during the OAuth2 token generation step to prevent unauthorized access.
