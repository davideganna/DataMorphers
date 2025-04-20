import json
import operator
from typing import Any, Literal, Dict, Union, List, Optional
from pydantic import BaseModel, Field, ValidationError, model_validator, field_validator

import narwhals as nw
import pandas as pd
from narwhals.typing import IntoFrame

from datamorphers.base import DataMorpher, DataMorpherError
from datamorphers.storage import dms

from datamorphers.constants.constants import SUPPORTED_TYPE_MAPPING


class CreateColumn(DataMorpher):
    class PyDanticValidator(BaseModel):
        column_name: str = Field(
            ..., min_length=1, description="Name of the new column"
        )
        value: Any = Field(..., description="Value to be assigned to the new column")

        @model_validator(mode="before")
        def check_value_type(cls, values: dict):
            value = values.get("value")
            if isinstance(value, str) and len(value) < 1:
                raise ValueError("Value must be a non-empty string")
            return values

    def __init__(self, *, column_name: str, value: Any):
        super().__init__()
        try:
            self.config = self.PyDanticValidator(column_name=column_name, value=value)
            self.column_name = self.config.column_name
            self.value = self.config.value
        except ValidationError as e:
            raise DataMorpherError(
                f"[{self.__class__.__name__}] Invalid config: {e}"
            ) from e

    @nw.narwhalify
    def _datamorph(self, df: IntoFrame) -> IntoFrame:
        """Adds a new column with a constant value to the dataframe."""
        df = df.with_columns(nw.lit(self.value).alias(self.column_name))
        return df


class CastColumnTypes(DataMorpher):
    class PyDanticValidator(BaseModel):
        cast_dict: Dict[str, str]

        @field_validator("cast_dict")
        def check_valid_types(cls, v: dict):
            for col, type_name in v.items():
                if type_name not in SUPPORTED_TYPE_MAPPING:
                    raise ValueError(
                        f"Unsupported type '{type_name}' for column '{col}'. Supported types are: {list(SUPPORTED_TYPE_MAPPING.keys())}."
                    )
            return v

    def __init__(self, *, cast_dict: dict):
        super().__init__()
        try:
            self.config = self.PyDanticValidator(cast_dict=cast_dict)
            self.cast_dict = self.config.cast_dict
        except ValidationError as e:
            raise DataMorpherError(
                f"[{self.__class__.__name__}] Invalid config: {e}"
            ) from e

    @nw.narwhalify
    def _datamorph(self, df: IntoFrame) -> IntoFrame:
        """Casts columns in the DataFrame to specific column types."""
        expr = [
            nw.col(i).cast(SUPPORTED_TYPE_MAPPING[c]) for i, c in self.cast_dict.items()
        ]
        df = df.with_columns(expr)

        return df


class ColumnsOperator(DataMorpher):
    class PyDanticValidator(BaseModel):
        first_column: str = Field(
            ..., min_length=1, description="First column to operate on"
        )
        second_column: str = Field(
            ..., min_length=1, description="Second column to operate on"
        )
        logic: str = Field(
            ...,
            description="The operation logic (e.g., 'add', 'sub') to apply between columns",
        )
        output_column: str = Field(
            ..., min_length=1, description="Name of the output column"
        )

        @field_validator("logic")
        def validate_logic(cls, v):
            valid_operations = ["add", "sub", "mul", "truediv"]
            if v not in valid_operations:
                raise ValueError(
                    f"Invalid logic operation. Valid operations are {valid_operations}"
                )
            return v

    def __init__(
        self, *, first_column: str, second_column: str, logic: str, output_column: str
    ):
        super().__init__()
        try:
            self.config = self.PyDanticValidator(
                first_column=first_column,
                second_column=second_column,
                logic=logic,
                output_column=output_column,
            )
            self.first_column = self.config.first_column
            self.second_column = self.config.second_column
            self.logic = self.config.logic
            self.output_column = self.config.output_column
        except ValidationError as e:
            raise DataMorpherError(
                f"[{self.__class__.__name__}] Invalid config: {e}"
            ) from e

    @nw.narwhalify
    def _datamorph(self, df: IntoFrame) -> IntoFrame:
        """
        Performs an operation on the values in the specified column by
        the values in another column.
        Renames the resulting column as 'output_column'.
        """
        operation = getattr(operator, self.logic)
        expr: nw.Expr = operation(
            nw.col(self.first_column), (nw.col(self.second_column))
        )
        df = df.with_columns(expr.alias(self.output_column))
        return df


class DropDuplicates(DataMorpher):
    class PyDanticValidator(BaseModel):
        subset: Optional[Union[List[str], str]] = Field(
            default=None, description="Columns to consider when dropping duplicates."
        )
        keep: str = Field(
            default="any",
            description="Which duplicates to keep. One of 'first', 'last', or 'any'.",
        )

        @field_validator("subset")
        def validate_subset(cls, v):
            if v is not None and not (isinstance(v, list) or isinstance(v, str)):
                raise ValueError(
                    "Subset must be either a list of column names or a single column name (string)."
                )
            return v

        @field_validator("keep")
        def validate_keep(cls, v):
            valid_values = ["first", "last", "any"]
            if v not in valid_values:
                raise ValueError(
                    f"Invalid value for 'keep'. Valid options are {valid_values}."
                )
            return v

    def __init__(self, *, subset: Union[List[str], str] = None, keep: str = "any"):
        super().__init__()
        try:
            self.config = self.PyDanticValidator(subset=subset, keep=keep)
            # Assign validated values
            self.subset = self.config.subset
            self.keep = self.config.keep
        except ValidationError as e:
            raise DataMorpherError(
                f"[{self.__class__.__name__}] Invalid config: {e}"
            ) from e

    @nw.narwhalify
    def _datamorph(self, df: IntoFrame) -> IntoFrame:
        """Drops duplicated rows."""
        if self.subset:
            # Drop duplicates only on a subset of columns
            df = df.unique(subset=self.subset, keep=self.keep)
        else:
            # Drop duplicates on the entire DataFrame
            df = df.unique()
        return df


class DropNA(DataMorpher):
    class PyDanticValidator(BaseModel):
        column_name: str = Field(
            ..., min_length=1, description="Name of the column to check for NaN values."
        )

    def __init__(self, *, column_name: str):
        super().__init__()
        try:
            self.config = self.PyDanticValidator(column_name=column_name)
            self.column_name = self.config.column_name
        except ValidationError as e:
            raise DataMorpherError(
                f"[{self.__class__.__name__}] Invalid config: {e}"
            ) from e

    @nw.narwhalify
    def _datamorph(self, df: IntoFrame) -> IntoFrame:
        """Drops rows with any NaN values."""
        df = df.drop_nulls(subset=self.column_name)
        return df


class FillNA(DataMorpher):
    class PyDanticValidator(BaseModel):
        column_name: str = Field(
            ..., description="Name of the column to fill NaN values."
        )
        value: Any = Field(
            ..., description="Value to replace NaN values in the specified column."
        )

        @model_validator(mode="before")
        def check_value_type(cls, values: dict):
            value = values.get("value")
            if isinstance(value, str) and len(value) < 1:
                raise ValueError("Value must be a non-empty string")
            return values

    def __init__(self, *, column_name: str, value: Any):
        super().__init__()
        try:
            self.config = self.PyDanticValidator(column_name=column_name, value=value)
            self.column_name = self.config.column_name
            self.value = self.config.value
        except ValidationError as e:
            raise DataMorpherError(
                f"[{self.__class__.__name__}] Invalid config: {e}"
            ) from e

    @nw.narwhalify
    def _datamorph(self, df: IntoFrame) -> IntoFrame:
        """Fills NaN values in the specified column with the provided value."""
        df = df.with_columns(
            nw.when(nw.col(self.column_name).is_nan())
            .then(self.value)
            .otherwise(nw.col(self.column_name))
            .alias(self.column_name)
        )
        return df


class FilterRows(DataMorpher):
    """
    Filter rows based on a condition.

    Parameters:
        first_column (str): Name of the column we want to compare.
        second_column (bool | float | int | str): If a column name is given,
            comparison will be done against the values present in that column.
            Otherwise, comparison will be done against the provided value.
        logic (str): Python operator.
    """

    class PyDanticValidator(BaseModel):
        first_column: str = Field(
            ..., description="Name of the first column to compare."
        )
        second_column: Union[bool, float, int, str] = Field(
            ..., description="Column name or value to compare against."
        )
        logic: str = Field(
            ..., description="Python operator for comparison (e.g., 'eq', 'lt', etc.)."
        )

        @field_validator("logic")
        def validate_logic(cls, v):
            valid_operations = ["eq", "gt", "ge", "lt", "le"]
            if v not in valid_operations:
                raise ValueError(
                    f"Invalid logic operation. Valid operations are {valid_operations}"
                )
            return v

    def __init__(
        self,
        *,
        first_column: str,
        second_column: Union[bool, float, int, str],
        logic: str,
    ):
        super().__init__()
        try:
            self.config = self.PyDanticValidator(
                first_column=first_column, second_column=second_column, logic=logic
            )
            self.first_column = self.config.first_column
            self.second_column = self.config.second_column
            self.logic = self.config.logic
        except ValidationError as e:
            raise DataMorpherError(
                f"[{self.__class__.__name__}] Invalid config: {e}"
            ) from e

    @nw.narwhalify
    def _datamorph(self, df: IntoFrame) -> IntoFrame:
        """Filters rows based on a condition."""
        operation = getattr(operator, self.logic)
        if self.second_column not in df.columns:
            col_to_compare = nw.lit(self.second_column)
        else:
            col_to_compare = nw.col(self.second_column)
        expr: nw.Expr = operation(nw.col(self.first_column), col_to_compare)
        df = df.filter(expr)
        return df


class FlatMultiIndex(DataMorpher):
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

    def __init__(self):
        super().__init__()

    def _datamorph(self, df: pd.DataFrame) -> pd.DataFrame:
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Input must be a Pandas DataFrame.")

        df.columns = df.columns.to_flat_index()
        df.columns = df.columns.map("_".join)
        return df


class MergeDataFrames(DataMorpher):
    """
    Pandas only.

    Merges two DataFrames based on specified columns and join type.
    """

    class PyDanticValidator(BaseModel):
        df_to_join: str
        join_cols: List[str]
        how: str = Field(..., pattern=r"^(left|right|inner|outer)$")
        suffixes: tuple[str, str]

        @model_validator(mode="before")
        def check_value_type(cls, values: dict):
            df_to_join = dms.get(values.get("df_to_join"))
            if not isinstance(df_to_join, pd.DataFrame):
                raise ValueError(
                    "Parameter 'df_to_join' must be a DataFrame."
                    f"Found type: {type(df_to_join)}."
                )
            return values

    def __init__(
        self,
        *,
        df_to_join: str,
        join_cols: list,
        how: str,
        suffixes: tuple[str, str],
    ):
        super().__init__()
        try:
            self.config = self.PyDanticValidator(
                df_to_join=df_to_join, join_cols=join_cols, how=how, suffixes=suffixes
            )
            self.df_to_join = dms.get(df_to_join)
            self.join_cols = self.config.join_cols
            self.how = self.config.how
            self.suffixes = self.config.suffixes
        except ValidationError as e:
            raise DataMorpherError(
                f"[{self.__class__.__name__}] Invalid config: {e}"
            ) from e

    def _datamorph(self, df: IntoFrame) -> IntoFrame:
        """Merges two DataFrames."""
        merged_df = pd.merge(
            left=df,
            right=self.df_to_join,
            on=self.join_cols,
            how=self.how,
            suffixes=self.suffixes,
        )
        return merged_df


class NormalizeColumn(DataMorpher):
    class PyDanticValidator(BaseModel):
        column_name: str = Field(
            ..., min_length=1, description="The name of the column to normalize"
        )
        output_column: str = Field(
            ...,
            min_length=1,
            description="The name of the output column for the normalized values",
        )

    def __init__(self, *, column_name: str, output_column: str):
        super().__init__()
        try:
            self.config = self.PyDanticValidator(
                column_name=column_name, output_column=output_column
            )
            self.column_name = self.config.column_name
            self.output_column = self.config.output_column
        except ValidationError as e:
            raise DataMorpherError(
                f"[{self.__class__.__name__}] Invalid config: {e}"
            ) from e

    @nw.narwhalify
    def _datamorph(self, df: IntoFrame) -> IntoFrame:
        """Normalize a numerical column in the dataframe using Z-score normalization."""

        df = df.with_columns(
            (
                (nw.col(self.column_name) - nw.col(self.column_name).mean())
                / nw.col(self.column_name).std()
            ).alias(self.output_column)
        )

        return df


class RemoveColumns(DataMorpher):
    class PyDanticValidator(BaseModel):
        columns_name: Union[str, List[str]] = Field(
            ..., description="List or a single column name to remove"
        )

        @field_validator("columns_name")
        def check_columns_name(cls, v):
            if isinstance(v, str):
                return [v]  # Convert to list if it's a single string
            elif isinstance(v, list):
                if not all(isinstance(i, str) for i in v):
                    raise ValueError(
                        "If 'columns_name' is a list, all elements must be strings."
                    )
                return v
            raise ValueError(
                "columns_name must be either a string or a list of strings."
            )

    def __init__(self, *, columns_name: Union[str, List[str]]):
        super().__init__()
        try:
            self.config = self.PyDanticValidator(columns_name=columns_name)
            self.columns_name = self.config.columns_name
        except ValidationError as e:
            raise DataMorpherError(
                f"[{self.__class__.__name__}] Invalid config: {e}"
            ) from e

    @nw.narwhalify
    def _datamorph(self, df: IntoFrame) -> IntoFrame:
        """Removes a specified column from the DataFrame."""
        df = df.drop(self.columns_name)
        return df


class RenameColumns(DataMorpher):
    class PyDanticValidator(BaseModel):
        rename_map: Dict[str, str] = Field(
            ..., description="Mapping of old column names to new column names"
        )

        @field_validator("rename_map")
        def check_rename_map(cls, v):
            if not all(
                isinstance(k, str) and isinstance(val, str) for k, val in v.items()
            ):
                raise ValueError("All keys and values in 'rename_map' must be strings.")
            return v

    def __init__(self, *, rename_map: Dict[str, str]):
        super().__init__()
        try:
            self.config = self.PyDanticValidator(rename_map=rename_map)
            self.rename_map = self.config.rename_map
        except ValidationError as e:
            raise DataMorpherError(
                f"[{self.__class__.__name__}] Invalid config: {e}"
            ) from e

    @nw.narwhalify
    def _datamorph(self, df: IntoFrame) -> IntoFrame:
        """Renames columns in the dataframe."""
        df = df.rename(self.rename_map)
        return df


class Rolling(DataMorpher):
    class PyDanticValidator(BaseModel):
        column_name: str = Field(
            ..., description="Name of the column to apply the rolling operation on"
        )
        how: Literal["mean", "std", "sum", "var"] = Field(
            ..., description="The rolling operation to apply"
        )
        window_size: int = Field(
            ..., gt=0, description="Window size for the rolling operation"
        )
        output_column: str = Field(
            ..., description="Name of the output column for the result"
        )

    def __init__(
        self,
        *,
        column_name: str,
        how: Literal["mean", "std", "sum", "var"],
        window_size: int,
        output_column: str,
    ):
        super().__init__()
        try:
            self.config = self.PyDanticValidator(
                column_name=column_name,
                how=how,
                window_size=window_size,
                output_column=output_column,
            )
            self.column_name = self.config.column_name
            self.how = self.config.how
            self.window_size = self.config.window_size
            self.output_column = self.config.output_column
        except ValidationError as e:
            raise DataMorpherError(
                f"[{self.__class__.__name__}] Invalid config: {e}"
            ) from e

    @nw.narwhalify
    def _datamorph(self, df: IntoFrame):
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


class SelectColumns(DataMorpher):
    class PyDanticValidator(BaseModel):
        columns_name: Union[str, List[str]] = Field(
            ..., description="Column(s) to select"
        )

    def __init__(self, *, columns_name: Union[str, List[str]]):
        super().__init__()

        # Validate with Pydantic
        try:
            self.config = self.PyDanticValidator(columns_name=columns_name)
            if isinstance(self.config.columns_name, str):
                self.columns_name = [self.config.columns_name]
            else:
                self.columns_name = self.config.columns_name
        except ValidationError as e:
            raise DataMorpherError(
                f"[{self.__class__.__name__}] Invalid config: {e}"
            ) from e

    @nw.narwhalify
    def _datamorph(self, df: IntoFrame) -> IntoFrame:
        """Selects columns from the DataFrame."""
        df = df.select(self.columns_name)
        return df


class ToLower(DataMorpher):
    class PyDanticValidator(BaseModel):
        columns_name: Union[str, List[str]] = Field(
            ..., description="Column(s) to convert to lowercase"
        )

    def __init__(self, *, columns_name: Union[str, List[str]]):
        super().__init__()
        try:
            self.config = self.PyDanticValidator(columns_name=columns_name)
            if isinstance(self.config.columns_name, str):
                self.columns_name = [self.config.columns_name]
            else:
                self.columns_name = self.config.columns_name
        except ValidationError as e:
            raise DataMorpherError(
                f"[{self.__class__.__name__}] Invalid config: {e}"
            ) from e

    @nw.narwhalify
    def _datamorph(self, df: IntoFrame) -> IntoFrame:
        df = df.with_columns(nw.col(self.columns_name).str.to_lowercase())
        return df


class ToUpper(DataMorpher):
    class PyDanticValidator(BaseModel):
        columns_name: Union[str, List[str]] = Field(
            ..., description="Column(s) to convert to uppercase"
        )

    def __init__(self, *, columns_name: Union[str, List[str]]):
        super().__init__()
        try:
            self.config = self.PyDanticValidator(columns_name=columns_name)
            if isinstance(self.config.columns_name, str):
                self.columns_name = [self.config.columns_name]  # Convert string to list
            else:
                self.columns_name = (
                    self.config.columns_name
                )  # Already a list of strings
        except ValidationError as e:
            raise DataMorpherError(
                f"[{self.__class__.__name__}] Invalid config: {e}"
            ) from e

    @nw.narwhalify
    def _datamorph(self, df: IntoFrame) -> IntoFrame:
        for col in self.columns_name:
            df = df.with_columns(
                nw.col(col).str.to_uppercase()
            )  # Note the correction here (using `col` instead of `self.columns_name`)

        return df
