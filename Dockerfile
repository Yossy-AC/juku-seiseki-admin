FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock* ./

# Install dependencies with uv
RUN uv sync --frozen

# Copy application code
COPY app/ ./app/
COPY static/ ./static/

# Expose port (Railway will use $PORT)
EXPOSE 8000

# Run application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
