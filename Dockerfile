# Minimal production-friendly image for Arthashree
FROM python:3.12-slim

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Create a non-root user
RUN useradd --create-home --shell /bin/bash arthuser
WORKDIR /home/arthuser/app

# System deps for pandas/numpy and common build tools
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential git curl ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy only dependency manifests first for Docker layer caching
COPY pyproject.toml pyproject.toml
COPY setup.cfg setup.cfg 2>/dev/null || true

# Install pip and project dependencies
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -e '.[dev]'

# Copy project files
COPY . /home/arthuser/app
RUN chown -R arthuser:arthuser /home/arthuser/app
USER arthuser

ENV PATH="/home/arthuser/.local/bin:${PATH}"

# Default entry: show help
ENTRYPOINT ["python", "-m"]
CMD ["arthashree.cli"]
