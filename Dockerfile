# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Node.js and npm
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install npx globally
RUN npm install -g npx

# Install prettier (if you're using it)
RUN npm install -g prettier@3.4.2

# Copy pyproject.toml for dependency installation
COPY pyproject.toml .

# Sync Python dependencies using uv
RUN uv sync

# Copy the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application using uvicorn
CMD ["uv", "pip", "install", "--force-reinstall", "uvicorn", "&&", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]