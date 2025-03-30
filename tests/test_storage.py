import importlib

import pytest

import datamorphers
import datamorphers.storage
from datamorphers.storage import dms


def test_set_and_get():
    dms.set("test_key", "test_value")
    assert dms.get("test_key") == "test_value"


def test_overwrite_warning(caplog: pytest.LogCaptureFixture):
    dms.set("test_key", "value1")
    assert "Attention! Key 'test_key' is already present" in caplog.text


def test_set_invalid_key():
    with pytest.raises(TypeError):
        dms.set(123, "value")


def test_get_nonexistent_key():
    with pytest.raises(KeyError) as exc_info:
        dms.get("missing_key")
    assert "Key 'missing_key' not found" in str(exc_info.value)


def test_isin():
    dms.set("existing_key", "some_value")
    assert dms.isin("existing_key") is True
    assert dms.isin("non_existent_key") is False


def test_list_keys():
    dms.set("key1", "value1")
    dms.set("key2", "value2")
    assert "key1" in dms.cache
    assert "key2" in dms.cache


def test_clear():
    dms.set("key1", "value1")
    dms.clear()
    assert len(dms.cache) == 0


def test_dms_is_singleton():
    """
    DataMorphersStorage is designed as a Singleton, so when it
        is instantiated in multiple modules, it needs to maintain
        the elements in the cache without resetting them.
    """
    # Try to create a new instance of dms. This will not create a new object.
    dms = datamorphers.storage.DataMorphersStorage()

    # Set a value in dms
    dms.set("A", 1)

    # Reload the module to simulate a fresh import
    importlib.reload(datamorphers)

    # Check that after reloading, the value is still present in dms
    assert "A" in dms.cache
