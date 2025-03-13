import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level (DEBUG, INFO, WARNING, etc.)
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],  # Ensures logs go to stdout (Jupyter)
)

logger = logging.getLogger(__name__)
logger.info("Datamorphers package initialized")
