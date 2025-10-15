FROM python:3.11-slim

WORKDIR /app

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den ganzen Ordner (nicht nur Inhalt)
COPY python_connector/ ./python_connector/

# Optional, hilft Python beim Finden des Pakets
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "python_connector.main:app", "--host", "0.0.0.0", "--port", "8000"]
