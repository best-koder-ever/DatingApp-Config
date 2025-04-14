# Stage 1: Build
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build-env
WORKDIR /app

# Copy the project file and restore dependencies
COPY UserService/UserService.csproj UserService/
RUN dotnet restore UserService/UserService.csproj

# Copy the entire project
COPY UserService/ UserService/  

# Build and publish the application
RUN dotnet publish UserService/UserService.csproj -c Release -o out

# Stage 2: Runtime
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app

# Copy the published files
COPY --from=build-env /app/out .

# Copy the public key
COPY public.key /app/public.key

# Expose port 8082
EXPOSE 8082

# Set the entry point for the application
ENTRYPOINT ["dotnet", "UserService.dll"]