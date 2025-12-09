In this project I built a Docker Compose stack consisting of four services:
frontend (Nginx), backend (Flask), Postgres, and Redis.

The services are separated into two networks — frontend and backend.

The web (Nginx) service lives on the frontend network, serves static frontend content, and forwards all /api requests to the backend via reverse proxy.

The backend service is connected to both networks.
This allows it to communicate with Nginx on the frontend network, and with Postgres and Redis on the backend network.

Redis and Postgres are isolated strictly inside the backend network, meaning the frontend can never directly access them.

Request Flow

The request flow works like this:

A user sends an HTTP request to Nginx.

Nginx either:

serves the request directly (static content), or
forwards the /api request to the backend.
The backend communicates with Postgres or Redis as needed.

The response then travels back the same path:
backend → Nginx → user

This ensures that neither the user nor the frontend ever directly access internal services like Postgres or Redis.

Healthchecks & Service Readiness

The backend exposes a /health endpoint, and Docker Compose uses:

depends_on:
  backend:
    condition: service_healthy


This ensures the frontend (Nginx) starts only after the backend is fully ready.

Postgres uses a named volume for persistent data, and network separation ensures security and clean layering within the stack.

Summary

This project demonstrates:

a layered multi-service architecture using Docker Compose
isolated networks (frontend and backend)
Nginx reverse proxy to the Flask backend
backend communication with Postgres and Redis
healthcheck-based orchestration
persistent Postgres storage
proper service separation and clean request flow

