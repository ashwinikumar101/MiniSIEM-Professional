# Use the official Python image
FROM python:3.13-slim

# Set the working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Expose Flask port
EXPOSE 5000

# Start the application
CMD ["python", "app.py"]