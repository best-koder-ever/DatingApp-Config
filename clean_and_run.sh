#!/bin/bash

# Stop and remove all containers
docker rm -f $(docker ps -aq)

# Remove all volumes
docker volume prune -f

# Remove unused networks
docker network prune -f

# Restart Docker Compose without rebuilding everything
docker-compose up -d
