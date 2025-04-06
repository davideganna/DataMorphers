import pytest
from datamorphers.base import DataMorpherError
from pydantic import ValidationError
from datamorphers.datamorphers import CreateColumn


def test_create_column_valid_string():
    # Test with a valid column_name and a non-empty string as value
    column = CreateColumn(column_name="valid_column", value="some_value")
    assert column.column_name == "valid_column"
    assert column.value == "some_value"


def test_create_column_valid_integer():
    # Test with a valid column_name and an integer as value
    column = CreateColumn(column_name="valid_column", value=123)
    assert column.column_name == "valid_column"
    assert column.value == 123


def test_create_column_valid_float():
    # Test with a valid column_name and a float as value
    column = CreateColumn(column_name="valid_column", value=123.45)
    assert column.column_name == "valid_column"
    assert column.value == 123.45


def test_create_column_empty_column_name():
    # Test with an empty column_name (this should raise an error)
    with pytest.raises(DataMorpherError, match="Invalid config"):
        CreateColumn(column_name="", value="some_value")


def test_create_column_column_name_is_none():
    # Test with column_name as None (this should raise an error)
    with pytest.raises(DataMorpherError, match="Invalid config"):
        CreateColumn(column_name=None, value="some_value")


def test_create_column_empty_value_string():
    # Test with an empty string for value (this should raise an error)
    with pytest.raises(DataMorpherError, match="Invalid config"):
        CreateColumn(column_name="valid_column", value="")


def test_create_column_value_is_none():
    # Test with None for value (this should pass as it can be any type)
    column = CreateColumn(column_name="valid_column", value=None)
    assert column.column_name == "valid_column"
    assert column.value is None


def test_create_column_invalid_value_type():
    # Test with an invalid value type (in this case, it would pass because any type is allowed)
    column = CreateColumn(column_name="valid_column", value={})  # Passing a dictionary
    assert column.column_name == "valid_column"
    assert column.value == {}


def test_create_column_invalid_column_name():
    # Test with invalid column_name (None value for column_name)
    with pytest.raises(DataMorpherError, match="Invalid config"):
        CreateColumn(column_name=None, value=123)


def test_create_column_value_non_string_with_min_length():
    # Check if it works when min_length check is applied to a string value
    with pytest.raises(DataMorpherError, match="Invalid config"):
        CreateColumn(column_name="valid_column", value="")
