FROM python:3.12-slim

WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY strands.py .
COPY common/ ./common/

# Expose the port
EXPOSE 8001

# Command to run the application
CMD ["uvicorn", "strands:app", "--host", "0.0.0.0", "--port", "8001"]