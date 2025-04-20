import pytest
from pydantic import ValidationError
from datamorphers.datamorphers import (
    CreateColumn,
    CastColumnTypes,
    ColumnsOperator,
    DropDuplicates,
    DropNA,
    FillNA,
    FilterRows,
    FlatMultiIndex,
    MergeDataFrames,
    NormalizeColumn,
    RemoveColumns,
    RenameColumns,
    Rolling,
    SelectColumns,
    ToLower,
    ToUpper,
)
from datamorphers.base import DataMorpherError
import pandas as pd
import narwhals as nw


# Test CreateColumn
def test_create_column_valid():
    morpher = CreateColumn(column_name="new_col", value="test")
    assert morpher.column_name == "new_col"
    assert morpher.value == "test"


def test_create_column_invalid_value():
    with pytest.raises(DataMorpherError):
        CreateColumn(column_name="new_col", value="")


# Test CastColumnTypes
def test_cast_column_types_valid():
    morpher = CastColumnTypes(cast_dict={"col1": "int8", "col2": "float32"})
    assert morpher.cast_dict == {"col1": "int8", "col2": "float32"}


def test_cast_column_types_invalid_type():
    with pytest.raises(DataMorpherError):
        CastColumnTypes(cast_dict={"col1": "unsupported_type"})


# Test ColumnsOperator
def test_columns_operator_valid():
    morpher = ColumnsOperator(
        first_column="col1", second_column="col2", logic="add", output_column="result"
    )
    assert morpher.first_column == "col1"
    assert morpher.second_column == "col2"
    assert morpher.logic == "add"
    assert morpher.output_column == "result"


def test_columns_operator_invalid_logic():
    with pytest.raises(DataMorpherError):
        ColumnsOperator(
            first_column="col1",
            second_column="col2",
            logic="invalid_op",
            output_column="result",
        )


# Test DropDuplicates
def test_drop_duplicates_valid():
    morpher = DropDuplicates(subset=["col1"], keep="first")
    assert morpher.subset == ["col1"]
    assert morpher.keep == "first"


def test_drop_duplicates_invalid_subset():
    with pytest.raises(DataMorpherError):
        DropDuplicates(subset=123)


def test_drop_duplicates_invalid_keep():
    with pytest.raises(DataMorpherError):
        DropDuplicates(subset=["col1"], keep="invalid_value")


# Test DropNA
def test_drop_na_valid():
    morpher = DropNA(column_name="col1")
    assert morpher.column_name == "col1"


def test_drop_na_invalid_column_name():
    with pytest.raises(DataMorpherError):
        DropNA(column_name="")


# Test FillNA
def test_fill_na_valid():
    morpher = FillNA(column_name="col1", value="fill_value")
    assert morpher.column_name == "col1"
    assert morpher.value == "fill_value"


def test_fill_na_invalid_value():
    with pytest.raises(DataMorpherError):
        FillNA(column_name="col1", value="")


# Test FilterRows
def test_filter_rows_valid():
    morpher = FilterRows(first_column="col1", second_column=5, logic="gt")
    assert morpher.first_column == "col1"
    assert morpher.second_column == 5
    assert morpher.logic == "gt"


def test_filter_rows_invalid_logic():
    with pytest.raises(DataMorpherError):
        FilterRows(first_column="col1", second_column=5, logic="invalid_op")


# Test FlatMultiIndex
def test_flat_multi_index_valid():
    morpher = FlatMultiIndex()
    # Define something that is not a DataFrame to test the error
    df = 123
    with pytest.raises(ValueError):
        morpher._datamorph(df)


# Test MergeDataFrames
def test_merge_data_frames_valid():
    df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    df = nw.from_native(df)
    morpher = MergeDataFrames(
        df_to_join=df, join_cols=["col1"], how="inner", suffixes="_1"
    )
    assert morpher.how == "inner"
    assert morpher.suffixes == "_1"


def test_merge_data_frames_invalid_how():
    df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    df = nw.from_native(df)
    with pytest.raises(DataMorpherError):
        MergeDataFrames(
            df_to_join=df,
            join_cols=["col1"],
            how="invalid",
            suffixes=("_left", "_right"),
        )


# Test NormalizeColumn
def test_normalize_column_valid():
    morpher = NormalizeColumn(column_name="col1", output_column="normalized_col")
    assert morpher.column_name == "col1"
    assert morpher.output_column == "normalized_col"


# Test RemoveColumns
def test_remove_columns_valid():
    morpher = RemoveColumns(columns_name=["col1", "col2"])
    assert morpher.columns_name == ["col1", "col2"]


def test_remove_columns_invalid():
    with pytest.raises(DataMorpherError):
        RemoveColumns(columns_name=123)


# Test RenameColumns
def test_rename_columns_valid():
    morpher = RenameColumns(rename_map={"col1": "new_col1"})
    assert morpher.rename_map == {"col1": "new_col1"}


def test_rename_columns_invalid():
    with pytest.raises(DataMorpherError):
        RenameColumns(rename_map={"col1": 123})


# Test Rolling
def test_rolling_valid():
    morpher = Rolling(
        column_name="col1", how="mean", window_size=3, output_column="rolling_mean"
    )
    assert morpher.column_name == "col1"
    assert morpher.how == "mean"
    assert morpher.window_size == 3
    assert morpher.output_column == "rolling_mean"


def test_rolling_invalid():
    with pytest.raises(DataMorpherError):
        Rolling(
            column_name="col1",
            how="invalid",
            window_size=3,
            output_column="rolling_mean",
        )


# Test SelectColumns
def test_select_columns_valid():
    morpher = SelectColumns(columns_name=["col1", "col2"])
    assert morpher.columns_name == ["col1", "col2"]


def test_select_columns_invalid():
    with pytest.raises(DataMorpherError):
        SelectColumns(columns_name=123)


# Test ToLower
def test_to_lower_valid():
    morpher = ToLower(columns_name=["col1", "col2"])
    assert morpher.columns_name == ["col1", "col2"]


def test_to_lower_invalid():
    with pytest.raises(DataMorpherError):
        ToLower(columns_name=123)


# Test ToUpper
def test_to_upper_valid():
    morpher = ToUpper(columns_name=["col1", "col2"])
    assert morpher.columns_name == ["col1", "col2"]


def test_to_upper_invalid():
    with pytest.raises(DataMorpherError):
        ToUpper(columns_name=123)
