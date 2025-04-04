from typing import Any

from datamorphers import logger

__all__ = ["dms"]


class DataMorphersStorage:
    """
    A Singleton-based, in-memory Storage.

    This class provides an in-memory key-value store designed
    to persist data across multiple module imports.
    It ensures that only a single instance of `DataMorphersStorage`
    exists throughout the application.

    Attributes:
        logger_msg (str): A prefix message used in log outputs.
        cache (dict): A dictionary that stores key-value pairs.

    Methods:
        clear() -> None:
            Resets all keys and values in the cache.

        get(key: str) -> Any:
            Retrieves the value associated with the given key. Raises a KeyError if
            the key does not exist.

        isin(key: str) -> bool:
            Checks if a key exists in the cache.

        list_keys() -> list:
            Returns a list of all keys currently stored in the cache.

        set(key: str, value: Any) -> None:
            Stores a value in the cache under the specified key. If the key already
            exists, it overwrites the value and logs a warning.

    Example Usage:
        >>> from datamorphers.storage import dms
        >>> dms.set("username", "Alice")
        >>> dms.get("username")
        'Alice'
        >>> dms.isin("username")
        True
        >>> dms.list_keys()
        ['username']
        >>> dms.clear()
        >>> dms.list_keys()
        []
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "cache"):
            self.logger_msg = "DataMorphers Storage -"
            self.cache = {}

    def clear(self) -> None:
        self.cache.clear()
        logger.info(f"{self.logger_msg} Storage cleared.")

    def get(self, key: str) -> Any:
        if key not in self.cache:
            available_keys = self.list_keys()
            raise KeyError(
                f"{self.logger_msg} Key '{key}' not found. "
                f"Available keys are: {available_keys}"
            )
        return self.cache[key]

    def isin(self, key: str) -> bool:
        return key in self.cache

    def list_keys(self) -> list[str]:
        return [key for key in self.cache]

    def set(self, key: str, value: Any) -> None:
        if type(key) is not str:
            raise TypeError(
                f"{self.logger_msg} Expected a string, but got {type(key)} instead."
            )
        if key in self.cache:
            logger.warning(
                f"{self.logger_msg} Attention! Key '{key}' is already present "
                "in DataMorphersStorage. The item will be overwritten."
            )
        logger.info(f"{self.logger_msg} Setting an object with key: {key}.")
        self.cache[key] = value


dms = DataMorphersStorage()
