from abc import ABC, abstractmethod

from narwhals.typing import FrameT


class DataMorpher(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def _datamorph(self, df: FrameT) -> FrameT:
        """Applies a transformation on the DataFrame."""
        pass


class DataMorpherError(Exception):
    """Base class for all DataMorpher errors."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
