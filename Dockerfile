# Use official Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port Railway expects
EXPOSE 5000

# Start the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:flask_app"]
