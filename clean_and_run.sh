#!/bin/bash

# Stop all running containers
for container in $(docker ps -q); do
  docker stop $container
done

# Remove all containers
for container in $(docker ps -a -q); do
  docker rm $container
done

# Remove all images
for image in $(docker images -q); do
  docker rmi $image
done

# Remove all volumes
for volume in $(docker volume ls -q); do
  docker volume rm $volume
done

# Remove all networks
for network in $(docker network ls -q); do
  docker network rm $network
done

# Build and run Docker Compose
docker-compose up --build -d