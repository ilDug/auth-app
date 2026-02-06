FROM python:3.13

# Set the working directory
WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the pyproject.toml and uv.lock (if exists) for dependency installation
COPY ./api/pyproject.toml ./
COPY ./api/uv.lock* ./

# Copy the openssl configuration file
COPY ./lib/config/openssl/openssl.cnf ./lib/openssl.cnf

# Install dependencies using uv
RUN uv sync --frozen --no-cache

# Copy the api directory contents into the container at /app
COPY ./api/ ./

# Copy the entrypoint script
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set the environment variables
ENV MONGO_HOST=db:27017
ENV MONGO_USER="authsuser"
ENV MONGO_DB="auth"
ENV FRONTEND_HOST="http://localhost:4200"
ENV MODE="PRODUCTION"
ENV REGISTRATION_BEHAVIOUR="ALLOW_ANYBODY"

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run app using fastapi with conditional mode (dev/run) based on MODE env variable
ENTRYPOINT ["/entrypoint.sh"]

# Run app in development mode with auto-reload
# CMD ["uv", "run", "fastapi", "dev", "main.py", "--host", "0.0.0.0", "--port", "8000"]

# HEALTHCHECK to monitor the health of the API service
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s CMD curl -f http://localhost:8000/health || exit 1