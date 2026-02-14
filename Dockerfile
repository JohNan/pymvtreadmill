FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    bluez \
    dbus \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install uv for dependency management
RUN pip install uv

# Set the working directory
WORKDIR /app

# Copy project files
COPY . .

# Install the project and its dependencies using uv
# --system to install into the system python environment
RUN uv pip install --system .

# Set entrypoint to the installed CLI tool
ENTRYPOINT ["pymvtreadmill"]

# Default arguments (show help if no args provided)
CMD ["--help"]
