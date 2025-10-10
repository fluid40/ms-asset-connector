# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy requirements first and install
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the app code
COPY python_connector/ ./python_connector/

# Expose the port Uvicorn will run on
EXPOSE 8000

# Run the app with Uvicorn
CMD ["python", "-m", "python_connector.main"]
