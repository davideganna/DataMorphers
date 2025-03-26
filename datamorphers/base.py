import pandas as pd
import logging
from abc import ABC, abstractmethod
from narwhals.typing import IntoFrame


class DataMorpher(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def _datamorph(self, df: IntoFrame) -> IntoFrame:
        """Applies a transformation on the DataFrame."""
        pass
