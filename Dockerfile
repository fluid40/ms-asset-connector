# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy requirements first and install
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the app code
COPY python_connector/ .

# Expose the port Uvicorn will run on
EXPOSE 8000

# Run the app with Uvicorn
CMD ["uvicorn", "python_connector.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
