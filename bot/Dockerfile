# Multi-stage build for Telegram bot
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Create non-root user for security
RUN groupadd -r botuser && useradd -r -g botuser botuser

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/botuser/.local

# Copy application code
COPY . .

# Set environment variables
ENV PATH=/home/botuser/.local/bin:$PATH
ENV PYTHONPATH=/app

# Change ownership to botuser
RUN chown -R botuser:botuser /app

# Switch to non-root user
USER botuser

# Health check (check if bot process is running)
HEALTHCHECK --interval=60s --timeout=30s --start-period=10s --retries=3 \
    CMD pgrep -f "python.*main.py" > /dev/null || exit 1

# Run the bot
CMD ["python", "main.py"]

