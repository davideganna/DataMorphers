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
    

class DropNA(DataMorpher):
    def __init__(self, column_name: str):
        self.column_name = column_name

    def _datamorph(self, df: pd.DataFrame) -> pd.DataFrame:
        """Drops rows with any NaN values."""
        df = df.dropna(subset=self.column_name)
        return df
    

class FillColumn(DataMorpher):
    def __init__(self, column_name: str, value: Any):
        self.column_name = column_name
        self.value = value

    def _datamorph(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fills NaN values in the specified column with the provided value."""
        df[self.column_name] = df[self.column_name].fillna(self.value)
        return df
    

class FilterRows(DataMorpher):
    def __init__(self, first_column: str, second_column: str, logic: str):
        """Logic can be e, g, l, ge, le."""
        self.first_column = first_column
        self.second_column = second_column
        self.logic = logic

    def _datamorph(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filters rows based on a condition in the specified column."""
        if self.logic == 'e':
            df = df.loc[
                df[self.first_column] == df[self.second_column]
            ]
        elif self.logic == 'g':
            df = df.loc[
                df[self.first_column] > df[self.second_column]
            ]
        elif self.logic == 'ge':
            df = df.loc[
                df[self.first_column] >= df[self.second_column]
            ]
        elif self.logic == 'l':
            df = df.loc[
                df[self.first_column] < df[self.second_column]
            ]
        elif self.logic == 'le':
            df = df.loc[
                df[self.first_column] <= df[self.second_column]
            ]
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
    

class RemoveColumn(DataMorpher):
    def __init__(self, column_name: str):
        self.column_name = column_name

    def _datamorph(self, df: pd.DataFrame) -> pd.DataFrame:
        """Removes a specified column from the DataFrame."""
        df = df.drop(columns=[self.column_name], errors='ignore')
        return df
    

class RenameColumn(DataMorpher):
    def __init__(self, old_column_name: str, new_column_name: str):
        self.old_column_name = old_column_name
        self.new_column_name = new_column_name

    def _datamorph(self, df: pd.DataFrame) -> pd.DataFrame:
        """Renames a column in the dataframe."""
        df = df.rename(columns={self.old_column_name: self.new_column_name})
        return df