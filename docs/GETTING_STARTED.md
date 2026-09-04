# Getting Started

Welcome to the **robotdegilim.xyz** backend! This guide will help you set up your local development environment.

## 🚀 Quickstart

This project uses [uv](https://github.com/astral-sh/uv), an extremely fast Python package and project manager. You do not need to install Python manually; `uv` handles it automatically based on the `.python-version` file.

### 1. Install Prerequisites
You only need `git` and `uv` installed on your machine.

**Mac / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone the Repository
```bash
git clone https://github.com/your-username/robotdegilim.xyz-backend.git
cd robotdegilim.xyz-backend
```

### 3. Configure the Environment
Copy the template environment file and add the required AWS S3 credentials so the backend can communicate with cloud storage.
```bash
# Mac/Linux:
cp .env.example .env

# Windows:
copy .env.example .env
```
*(Open the newly created `.env` file and fill in `S3_ACCESS_KEY_ID` and `S3_SECRET_ACCESS_KEY`)*

### 4. Install Dependencies
Tell `uv` to create the virtual environment and install all dependencies strictly from `uv.lock`. This takes less than a second!
```bash
uv sync
```

### 5. Run the Application
We have provided a cross-platform CLI runner called `start.py`.

**Run ONLY the API Server:**
```bash
uv run start.py server
```
**Run ONLY the Background Worker:**
```bash
uv run start.py worker
```
**Run BOTH (Recommended for Local Dev):**
```bash
uv run start.py all
```

---

## 🏗️ Architecture Overview

This backend is intentionally decoupled into two separate systems that communicate via AWS S3:

1. **The Server (FastAPI):** Handles lightweight HTTP requests from the frontend.
2. **The Worker (Infinite Loop):** A robust background daemon that continuously polls a queue in S3. It executes heavy jobs (like scraping the 170+ departments from the METU SIS system) asynchronously without blocking the API.

## ☁️ Production Deployment (Fly.io)

In production on Fly.io, we utilize **Process Groups** in the `fly.toml` file. This allows Fly.io to spin up the Server and the Worker as completely isolated VMs from the exact same codebase. 

*(Note: Never run `uv run start.py all` in production, as combining the API and the Worker into a single container defeats horizontal scaling and crash-isolation!)*
