import logging

# Prevent duplicate log handlers
if not logging.getLogger("datamorphers").hasHandlers():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
    )

logger = logging.getLogger("datamorphers")
logger.debug("DataMorphers logging initialized!")
