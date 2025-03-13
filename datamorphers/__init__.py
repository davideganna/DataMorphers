import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to see all messages
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],  # Ensure logs go to stdout
)

# Create a logger instance for the package
logger = logging.getLogger("datamorphers")

# Optional: Prevent duplicate logs
if not logger.hasHandlers():
    logger.addHandler(logging.StreamHandler())

logger.setLevel(logging.DEBUG)

logger.info("Datamorphers package initialized")
