# Start with an official Python image. "Slim" = smaller size, "bookworm" = Debian version
FROM python:3.11-slim-bookworm

# All commands from here run inside /app inside the container
WORKDIR /app

# Create a normal user called "appuser" so we don't run as root (which is dangerous)
RUN useradd -m -u 1000 appuser

# Copy requirements first (before the rest of the code)
# Why? Docker caches each step. If requirements.txt hasn't changed,
# Docker skips the pip install on the next build, making it much faster
COPY --chown=appuser:appuser requirements.txt .

# Install Python dependencies
# --no-cache-dir = don't store the download cache, keeps image size smaller
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the application code
# --chown makes appuser the owner of these files, not root
COPY --chown=appuser:appuser . .

# Switch to appuser — everything from here runs as a normal, limited user
# If someone hacks the app, they get appuser's limited permissions, not root
USER appuser

# Tell Docker the app listens on port 8000
# Note: this is documentation only, it doesn't actually open the port
EXPOSE ${PORT:-8000}

# The command that runs when the container starts
# Starts the FastAPI app, accessible from outside the container (0.0.0.0)
# CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["sh", "-c", "uvicorn src.api:app --host 0.0.0.0 --port ${PORT:-8000}"]
# This reads the PORT env variable, and falls back to 8000 if not set