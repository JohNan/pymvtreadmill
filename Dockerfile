# Use a multi-stage build to keep the final image small
# Builder stage
FROM python:3.13-slim AS builder

# Install build dependencies
# build-essential: gcc, make, etc.
# python3-dev: Python header files
# pkg-config: For finding libraries
# libglib2.0-dev, libdbus-1-dev: Required for building dbus-fast (bleak dependency)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    pkg-config \
    libglib2.0-dev \
    libdbus-1-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv for dependency management
RUN pip install uv

# Set the working directory
WORKDIR /app

# Copy dependency definition files first to leverage Docker cache
COPY pyproject.toml uv.lock ./

# Create a virtual environment
RUN uv venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Export dependencies from lockfile to ensure reproducible builds
RUN uv export --frozen --no-dev --format requirements-txt > requirements.txt

# Install dependencies into the virtual environment
RUN uv pip install -r requirements.txt

# Copy the rest of the project files
COPY . .

# Install the project itself (non-editable, no dependencies since they are already installed)
RUN uv pip install --no-deps .

# Runtime stage
FROM python:3.13-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    bluez \
    dbus \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Set environment variables to use the virtual environment
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Set entrypoint to the installed CLI tool
ENTRYPOINT ["pymvtreadmill"]

# Default arguments (show help if no args provided)
CMD ["--help"]
