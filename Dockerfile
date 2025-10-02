# Use Windows-based Python image for proper Word/PDF conversion
FROM python:3.11-windowsservercore

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir templates outputs

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Start command
CMD ["python", "working_fastapi.py"]
