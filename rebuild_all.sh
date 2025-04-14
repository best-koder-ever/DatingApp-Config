#!/bin/bash

# Stop and remove all containers
docker rm -f $(docker ps -aq)

# Remove all volumes
docker volume prune -f

# Remove unused networks
docker network prune -f

# rebuild ALL
docker-compose up --build