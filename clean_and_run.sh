#!/bin/bash

# Stop all running containers except MySQL
for container in $(docker ps -q); do
  if [[ $(docker inspect --format='{{.Config.Image}}' $container) != *"mysql"* ]]; then
    docker stop $container
  fi
done

# Remove all containers except MySQL
for container in $(docker ps -a -q); do
  if [[ $(docker inspect --format='{{.Config.Image}}' $container) != *"mysql"* ]]; then
    docker rm $container
  fi
done

# Remove all images except MySQL
for image in $(docker images -q); do
  if [[ $(docker inspect --format='{{.RepoTags}}' $image) != *"mysql"* ]]; then
    docker rmi $image
  fi
done

# Remove all volumes except those used by MySQL
for volume in $(docker volume ls -q); do
  if [[ $volume != *"mysql"* ]]; then
    docker volume rm $volume
  fi
done

# Remove all networks except those used by MySQL
for network in $(docker network ls -q); do
  if [[ $network != *"mysql"* ]]; then
    docker network rm $network
  fi
done

# Build and run Docker Compose
docker-compose up --build -d  