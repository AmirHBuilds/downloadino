# Mirrorino

> A self-hosted GitHub mirror that kept open-source software accessible during Iran's nationwide Internet outage.

🚀 Used over **6,000,000 times** during the 2026 Iran internet disruption.

<p align="center">
  <img width="1125" height="630" alt="Screenshot (133)" src="https://github.com/user-attachments/assets/e31a70ec-f493-44da-9aa3-2438f6ea7b5c" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688">
  <img src="https://img.shields.io/badge/Nuxt-Frontend-00DC82">
  <img src="https://img.shields.io/badge/PostgreSQL-Database-336791">
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED">
  <img src="https://img.shields.io/badge/License-MIT-blue">
</p>

## Why Mirrorino?

When access to GitHub became unreliable during Iran's nationwide Internet outage,
developers still needed packages, repositories and documentation.

Mirrorino was built to solve exactly that problem.

Instead of relying on GitHub availability, organizations can deploy their own mirror in minutes.

During the outage Mirrorino served more than

# 6,000,000 requests

making open-source repositories available even when GitHub was unreachable.

## See it in action

<img width="1280" height="720" alt="Timeline 1 (1)" src="https://github.com/user-attachments/assets/683fe03f-ee4b-449a-a940-a2fc7b606e02" />

## ✨ Features

- 📦 Self-hosted GitHub-like repository platform
- 🔍 Fast repository search
- 📂 File browser with directory navigation
- 📄 Markdown & code preview
- 👤 Authentication and user management
- ⚡ FastAPI REST API
- 🐳 One-command Docker deployment
- 🌐 Responsive modern UI
- 🔒 Reverse proxy with Nginx

## Screenshots

### Repository View

<img width="100%" alt="Screenshot (208)" src="https://github.com/user-attachments/assets/fa584e6b-3a8c-4373-a8f6-9e3055cb366c" />

### Admin Dashboard

<img width="100%" alt="Screenshot (197)" src="https://github.com/user-attachments/assets/0a349f84-893b-4dec-b729-67ce60e34768" />

### User Management

<img width="100%" alt="Screenshot (199)" src="https://github.com/user-attachments/assets/e4ec6d4e-421a-48f3-9353-d8f269ba910b" />

### Statistics

<img width="100%" alt="Screenshot (198)" src="https://github.com/user-attachments/assets/44c9bd3e-8bc3-43bb-9cf2-7689e5dec0e2" />

## Structure
```
mirrorino/
├── backend/     FastAPI — api.mirrorino.com
├── frontend/    Nuxt 3 — mirrorino.com
├── nginx/       Reverse proxy
└── docker-compose.yml
```

## Quick start

```bash
# 1. Copy and fill the single env file
cp .env.example .env

# 2. Start everything from Docker Hub images
git clone https://github.com/AmirHBuilds/mirrorino
docker compose up -d

# 3. API docs available at:
#    https://api.mirrorino.com/api/docs
```

### Offline icon mode (no public internet needed)

This project is configured to load icons from local files under `frontend/icons/mdi` via Nuxt Icon custom collections.
No Iconify API access is required.


## Default admin
Username: admin  
Password: set in `.env` → `SUPERADMIN_PASSWORD`
