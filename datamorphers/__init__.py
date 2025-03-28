import importlib
import logging

__all__ = ["custom_datamorphers", "logger"]


def initialize_logger():
    """
    Initializes the logger for the DataMorphers package.
    Ensures there are no duplicate handlers.
    """
    logger = logging.getLogger("datamorphers")

    # Prevent duplicate log handlers
    if not logger.hasHandlers():
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            force=True,
        )
    logger.debug("DataMorphers logging initialized.")
    return logger


def load_custom_datamorphers():
    """
    Tries to import the custom_datamorphers module, if it exists.
    """
    try:
        custom_datamorphers = importlib.import_module("custom_datamorphers")
        logger.info("Successfully imported module custom_datamorphers.")
    except ModuleNotFoundError:
        logger.info(
            "Module custom_datamorphers not found. "
            "Custom DataMorphers implementations will not be loaded.\n"
        )
        custom_datamorphers = None
    return custom_datamorphers


# Initialize logger
logger = initialize_logger()

# Load custom DataMorphers if available
custom_datamorphers = load_custom_datamorphers()
