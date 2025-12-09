#!/usr/bin/env bash
set -e

echo "Shutting down stack"
docker compose down

echo "Building stack"
docker compose build

echo "Running stack"
docker compose up -d

echo "Stats for stack"
docker compose ps
