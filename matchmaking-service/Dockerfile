# Stage 1: Build
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build-env
WORKDIR /app

# Copy the project file and restore dependencies
COPY MatchmakingService/MatchmakingService.csproj MatchmakingService/
RUN dotnet restore MatchmakingService/MatchmakingService.csproj

# Copy the entire project
COPY MatchmakingService/ MatchmakingService/

# Build and publish the application
RUN dotnet publish MatchmakingService/MatchmakingService.csproj -c Release -o out

# Stage 2: Runtime
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app

# Copy the published files
COPY --from=build-env /app/out .

# Expose port 8083
EXPOSE 8083

# Set the entry point for the application
ENTRYPOINT ["dotnet", "MatchmakingService.dll"]