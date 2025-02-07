# Use an official Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install curl and other necessary utilities
RUN apt-get update && apt-get install -y curl && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Ensure uv is available in the shell
ENV PATH="/root/.local/bin:$PATH"

# Copy the project files to the container
COPY . .

# Sync dependencies using uv
RUN uv sync

# Expose the FastAPI port
EXPOSE 8000

# Use uv to run uvicorn explicitly
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
