# Task Manager

A simple and intuitive task manager built with Python (FastAPI), Vue.js, and PostgreSQL.

## 🚀 Features

- **User Authentication:** Secure and modern user management with JWT.
- **Project Management:** Create and manage projects.
- **Task Board:** A visual task board (Kanban style) with drag-and-drop functionality to change task status.
- **Role-Based Access:** Assign users to projects and control permissions.

## 🛠️ Tech Stack

- **Backend:**
    - **FastAPI:** High-performance Python API framework.
    - **SQLAlchemy:** SQL Toolkit and Object-Relational Mapper (ORM).
    - **PostgreSQL:** Robust relational database.
- **Frontend:**
    - **Vue.js:** Progressive JavaScript framework for building user interfaces.
    - **Vite:** Next-generation frontend tooling.
- **Tooling:**
    - **Docker & Docker Compose:** Containerization for easy setup and deployment.
    - **uv:** A blazing-fast Python package installer and dependency resolver.
    - **Alembic:** Database migrations tool.

## 🏗️ Project Structure

- `backend/`: Contains the FastAPI application.
- `frontend/`: Contains the Vue.js single-page application.
- `docker-compose-dev.yml`: Configuration for the development environment (hot-reloading, DB).
- `docker-compose.yml`: Configuration for the production environment.
- `Dockerfile.backend`: Instructions to build the backend Docker image.
- `.env.example`: A template for environment variables.

## ⚙️ Getting Started (Development)

1.  **Clone the repository:**


2.  **Create `.env` file:**
    Copy the example file and fill in your variables.
    ```bash
    cp .env.example .env
    ```

3.  **Start the services:**
    This command will build the Docker images and start the backend and PostgreSQL containers. The backend will have hot-reloading enabled.
    ```bash
    docker compose -f docker-compose-dev.yml up --build
    ```

4.  **Run frontend (coming soon):**
    Instructions for the frontend will be added here once the setup is complete.

The backend API will be available at `http://localhost:8000`. You can access the auto-generated documentation at `http://localhost:8000/docs`.

