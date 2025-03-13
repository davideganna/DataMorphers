import logging

# Prevent duplicate log handlers
if not logging.getLogger("datamorphers").hasHandlers():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        force=True,
    )

logger = logging.getLogger("datamorphers")
logger.debug("Datamorphers logging initialized!")
