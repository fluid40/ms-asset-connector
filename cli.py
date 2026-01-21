import logging

from logging_handler import initialize_logging
from python_connector.main import start_app

if __name__ == "__main__":
    """Run the FastAPI application."""
    initialize_logging(logging.DEBUG)
    start_app()
