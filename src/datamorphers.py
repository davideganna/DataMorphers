import pandas as pd
from abc import ABC, abstractmethod
from typing import Any


class DataMorpher(ABC):
    @abstractmethod
    def _datamorph(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies a transformation on the DataFrame.
        Each concrete class must implement this method.
        """
        pass


class CreateColumn(DataMorpher):
    def __init__(self, column_name: str, value: Any):
        self.column_name = column_name
        self.value = value

    def _datamorph(self, df):
        """Adds a new column with a constant value to the dataframe."""
        df[self.column_name] = self.value
        return df
    

class MultiplyColumns(DataMorpher):
    def __init__(self, first_column: str, second_column: str, output_column: str):
        self.first_column = first_column
        self.second_column = second_column
        self.output_column = output_column

    def _datamorph(self, df: pd.DataFrame) -> pd.DataFrame:
        """Multiplies the values in the specified column by another column.
        Renames the resulting column as 'output_column'.
        """
        df[self.output_column] = df[self.first_column] * df[self.second_column]
        return df


class NormalizeColumn(DataMorpher):
    def __init__(self, column_name: str, output_column: str):
        self.column_name = column_name
        self.output_column = output_column

    def _datamorph(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize a numerical column in the dataframe using Z-score normalization."""
        df[self.output_column] = (df[self.column_name] - df[self.column_name].mean()) / df[self.column_name].std()
        return df