import pandas as pd
from abc import ABC, abstractmethod

class DataMorpher(ABC):
    @staticmethod
    def _handle_args(args: dict, extra_dfs: dict=None):
        """Handle arguments in diferent ways when evaluated at runtime."""
        return args

    @abstractmethod
    def _datamorph(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applies a transformation on the DataFrame."""
        pass
