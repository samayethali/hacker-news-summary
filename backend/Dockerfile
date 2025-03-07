# Build stage
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Install pip and curl in one layer, clean apt cache
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip==23.3.1

# Copy only requirements file first for better cache utilization
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim

# Install only curl for healthcheck
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser

# Set working directory
WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Set correct PATH for the packages
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy only necessary application files
COPY main.py .
COPY ./entrypoint.sh /entrypoint.sh

# Set correct ownership
RUN chown -R appuser:appuser /app /home/appuser && \
    chmod +x /entrypoint.sh

# Switch to non-root user
USER appuser

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Set container startup command 
# The entrypoint script performs initialization and then executes the CMD
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
