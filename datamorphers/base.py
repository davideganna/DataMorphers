import pandas as pd
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class DataMorpher(ABC):
    def __init__(self):
        pass

    @staticmethod
    def _handle_args(args: dict, extra_dfs: dict = None):
        """Handle arguments in different ways when evaluated at runtime."""
        return args

    @abstractmethod
    def _datamorph(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applies a transformation on the DataFrame."""
        pass
