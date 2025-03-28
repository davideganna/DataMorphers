import pandas as pd
import pyarrow as pa
import narwhals as nw
import json
import operator
from narwhals.typing import FrameT
from typing import Any, Literal
from datamorphers.base import DataMorpher


class CreateColumn(DataMorpher):
    def __init__(self, *, column_name: str, value: Any):
        super().__init__()
        self.column_name = column_name
        self.value = value

    @nw.narwhalify
    def _datamorph(self, df: FrameT) -> FrameT:
        """Adds a new column with a constant value to the dataframe."""
        df = df.with_columns(nw.lit(self.value).alias(self.column_name))
        return df


class CastColumnTypes(DataMorpher):
    def __init__(self, *, cast_dict: dict):
        super().__init__()
        self.cast_dict = cast_dict

    @nw.narwhalify
    def _datamorph(self, df: FrameT) -> FrameT:
        """Casts columns in the DataFrame to specific column types."""
        from datamorphers.constants import SUPPORTED_TYPE_MAPPING

        df = df.with_columns(
            nw.col(i).cast(SUPPORTED_TYPE_MAPPING[c]) for i, c in self.cast_dict.items()
        )

        return df


class ColumnsOperator(DataMorpher):
    def __init__(
        self, *, first_column: str, second_column: str, logic: str, output_column: str
    ):
        super().__init__()
        self.first_column = first_column
        self.second_column = second_column
        self.logic = logic
        self.output_column = output_column

    @nw.narwhalify
    def _datamorph(self, df: FrameT) -> FrameT:
        """
        Performs an operation on the values in the specified column by
            the values inanother column.
        Renames the resulting column as 'output_column'.
        """
        operation = getattr(operator, self.logic)
        expr: nw.Expr = operation(
            nw.col(self.first_column), (nw.col(self.second_column))
        )
        df = df.with_columns(expr.alias(self.output_column))
        return df


class DeleteDataFrame(DataMorpher):
    def __init__(self, *, file_name: list | str):
        super().__init__()
        self.file_name = file_name if type(file_name) is list else [file_name]

    def _datamorph(self, df: FrameT) -> FrameT:
        """
        Deletes a DataFrame (or a list of DataFrames) previously saved using pickle.
        """
        import os.path

        for file in self.file_name:
            if os.path.isfile(f"{file}.pkl"):
                os.remove(f"{file}.pkl")

        return df


class DropDuplicates(DataMorpher):
    def __init__(self, subset: list | str = None, keep: str = "any"):
        super().__init__()
        if subset is None:
            self.subset = None
        elif isinstance(subset, list):
            self.subset = subset
        else:
            self.subset = [subset]
        self.keep = keep

    @nw.narwhalify
    def _datamorph(self, df: FrameT) -> FrameT:
        """Drops duplicated rows."""
        if self.subset:
            # Drop duplicates only on a subset of columns
            df = df.unique(subset=self.subset, keep=self.keep)
        else:
            # Drop duplicates on the entire DataFrame
            df = df.unique()
        return df


class DropNA(DataMorpher):
    def __init__(self, *, column_name: str):
        super().__init__()
        self.column_name = column_name

    @nw.narwhalify
    def _datamorph(self, df: FrameT) -> FrameT:
        """Drops rows with any NaN values."""
        df = df.drop_nulls(subset=self.column_name)
        return df


class FillNA(DataMorpher):
    def __init__(self, *, column_name: str, value: Any):
        super().__init__()
        self.column_name = column_name
        self.value = value

    @nw.narwhalify
    def _datamorph(self, df: FrameT) -> FrameT:
        """Fills NaN values in the specified column with the provided value."""
        df = df.with_columns(
            nw.when(nw.col(self.column_name).is_nan())
            .then(self.value)
            .otherwise(nw.col(self.column_name))
            .alias(self.column_name)
        )
        return df


class FilterRows(DataMorpher):
    def __init__(self, *, first_column: str, second_column: str, logic: str):
        """Logic is python standard operator"""
        super().__init__()
        self.first_column = first_column
        self.second_column = second_column
        self.logic = logic

    @nw.narwhalify
    def _datamorph(self, df: FrameT) -> FrameT:
        """Filters rows based on a condition in the specified column."""
        operation = getattr(operator, self.logic)
        expr: nw.Expr = operation(nw.col(self.first_column), nw.col(self.second_column))
        df = df.filter(expr)
        return df


class FlatMultiIndex(DataMorpher):
    def __init__(self):
        super().__init__()

    def _datamorph(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Pandas only.

        Flattens the multi-index columns, leaving intact single index columns.
        After being flattened, the columns will be joined by an underscore.

        Example:
            Before:
                MultiIndex([('A', 'B'), ('C', 'D'), 'E']
            After:
                Index(['A_B', 'C_D', 'E']
        """

        df.columns = df.columns.to_flat_index()
        df.columns = df.columns.map("_".join)
        return df


class MergeDataFrames(DataMorpher):
    def __init__(self, df_to_join: dict, join_cols: list, how: str, suffixes: list):
        super().__init__()
        # Deserialize the DataFrame
        self.df_to_join = pd.read_json(json.dumps(df_to_join))
        self.join_cols = join_cols
        self.how = how
        self.suffixes = suffixes

    def _datamorph(self, df: pd.DataFrame) -> pd.DataFrame:
        """Merges two DataFrames."""
        merged_df = pd.merge(
            df,
            self.df_to_join,
            on=self.join_cols,
            how=self.how,
            suffixes=self.suffixes,
        )
        return merged_df


class NormalizeColumn(DataMorpher):
    def __init__(self, column_name: str, output_column: str):
        super().__init__()
        self.column_name = column_name
        self.output_column = output_column

    def _datamorph(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize a numerical column in the dataframe using Z-score normalization."""
        df[self.output_column] = (
            df[self.column_name] - df[self.column_name].mean()
        ) / df[self.column_name].std()
        return df


class RemoveColumns(DataMorpher):
    def __init__(self, columns_name: list | str):
        super().__init__()
        self.columns_name = (
            columns_name if type(columns_name) is list else [columns_name]
        )

    @nw.narwhalify
    def _datamorph(self, df: FrameT) -> FrameT:
        """Removes a specified column from the DataFrame."""
        df = df.drop(self.columns_name)
        return df


class RenameColumns(DataMorpher):
    def __init__(self, *, cols_mapping: dict):
        super().__init__()
        self.cols_mapping = cols_mapping

    @nw.narwhalify
    def _datamorph(self, df: FrameT) -> FrameT:
        """Renames a column in the dataframe."""
        df = df.rename(self.cols_mapping)
        return df


class Rolling(DataMorpher):
    def __init__(
        self,
        *,
        column_name: str,
        how: Literal["mean", "std", "sum", "var"],
        window_size: int,
        output_column: str,
    ):
        super().__init__()
        self.column_name = column_name
        self.how = how
        self.window_size = window_size
        self.output_column = output_column

    @nw.narwhalify
    def _datamorph(self, df: FrameT):
        """Computes rolling operation on a column."""
        col = df.get_column(self.column_name)
        if self.how == "mean":
            rolling_col = col.rolling_mean(self.window_size)
        elif self.how == "std":
            rolling_col = col.rolling_std(self.window_size)
        elif self.how == "sum":
            rolling_col = col.rolling_sum(self.window_size)
        elif self.how == "var":
            rolling_col = col.rolling_var(self.window_size)
        df = df.with_columns(rolling_col.alias(self.output_column))
        return df


class SaveDataFrame(DataMorpher):
    def __init__(self, file_name: str):
        super().__init__()
        self.file_name = file_name

    def _datamorph(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Pandas only.

        Saves a DataFrame using pickle.

        If you wish to later remove the pickle file, call 'DeleteDataFrame'
            at the end of the pipeline.
        """
        df.to_pickle(f"{self.file_name}.pkl")
        return df


class SelectColumns(DataMorpher):
    def __init__(self, columns_name: list | str):
        super().__init__()
        self.columns_name = (
            columns_name if type(columns_name) is list else [columns_name]
        )

    @nw.narwhalify
    def _datamorph(self, df: FrameT) -> FrameT:
        """Selects columns from the DataFrame."""
        df = df.select(self.columns_name)
        return df
