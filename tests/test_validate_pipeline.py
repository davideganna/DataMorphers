from unittest.mock import patch

import pytest

from datamorphers import datamorphers
from datamorphers.pipeline_loader import validate_pipeline_config


class MockDataMorpher:
    """Mock DataMorpher for testing."""

    def __init__(self, *, column_name: str, value: int):
        self.column_name = column_name
        self.value = value


@pytest.fixture
def mock_fillna():
    """Fixture to patch the FillNA DataMorpher."""
    with patch.object(datamorphers, "FillNA", new=MockDataMorpher):
        yield


def test_valid_pipeline(mock_fillna):
    """Test that a valid pipeline passes validation."""
    config = {
        "pipeline_name": "test_pipeline",
        "test_pipeline": [{"FillNA": {"column_name": "A", "value": 0}}],
    }

    # Should not raise any exception
    validate_pipeline_config(config)


def test_missing_pipeline_name(mock_fillna):
    """Test that missing required arguments raises an error."""
    config = {"test_pipeline": [{"FillNA": {"column_name": "A", "value": 0}}]}

    with pytest.raises(
        ValueError, match="Missing 'pipeline_name' in pipeline configuration."
    ):
        validate_pipeline_config(config)


def test_invalid_pipeline_step():
    """Test that an invalid pipeline step format raises an error."""
    config = {"pipeline_name": "test_pipeline", "test_pipeline": [123]}

    with pytest.raises(ValueError, match="Invalid pipeline step format: 123"):
        validate_pipeline_config(config)


def test_missing_required_argument(mock_fillna):
    """Test that missing required arguments raises an error."""
    config = {
        "pipeline_name": "test_pipeline",
        "test_pipeline": [{"FillNA": {"column_name": "A"}}],  # Missing 'value'
    }

    with pytest.raises(ValueError, match="Missing required arguments for FillNA"):
        validate_pipeline_config(config)


def test_unexpected_argument(mock_fillna):
    """Test that extra arguments raise an error."""
    config = {
        "pipeline_name": "test_pipeline",
        "test_pipeline": [
            {"FillNA": {"column_name": "A", "value": 0, "extra_param": 123}}
        ],
    }

    with pytest.raises(ValueError, match="Unexpected arguments for FillNA"):
        validate_pipeline_config(config)


def test_unknown_datamorpher():
    """Test that an unknown DataMorpher raises an error."""
    config = {
        "pipeline_name": "test_pipeline",
        "test_pipeline": [{"UnknownMorpher": {"column_name": "A", "value": 0}}],
    }

    with pytest.raises(ValueError, match="Unknown DataMorpher"):
        validate_pipeline_config(config)
