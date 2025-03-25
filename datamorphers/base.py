import pandas as pd
import logging
from abc import ABC, abstractmethod


class DataMorpher(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def _datamorph(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applies a transformation on the DataFrame."""
        pass
