from abc import ABC, abstractmethod

from narwhals.typing import FrameT

from pydantic import BaseModel


class DataMorpher(ABC):
    class PyDanticValidator(BaseModel):
        """Pydantic validator for DataMorpher classes."""

    def __init__(self):
        pass

    def __init_subclass__(cls, **kwargs):  # pragma: no cover
        """Checks if the subclass implements a PyDanticValidator class."""
        super().__init_subclass__(**kwargs)
        if "PyDanticValidator" not in cls.__dict__:
            raise TypeError(
                f"{cls.__name__} must define its own `PyDanticValidator` class."
            )

    @abstractmethod
    def _datamorph(self, df: FrameT) -> FrameT:
        """Applies a transformation on the DataFrame."""
        pass


class DataMorpherError(Exception):
    """Base class for all DataMorpher errors."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
