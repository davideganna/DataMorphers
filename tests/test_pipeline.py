# pytest -s -v --disable-pytest-warnings

import pandas as pd
import numpy as np
from src.pipeline_loader import get_pipeline_config, run_pipeline

YAML_PATH = 'tests/test_pipeline.yaml'

def generate_mock_df():
    df = pd.DataFrame(
        {
            'A': [1, 2, 3],
            'B': [4, 5, np.nan],
            'NA_col': ['a', 'b', np.nan],
            'ToRemove': ['a', 'b', 'c'],
            'ToRename': [1, 2, 3],
        }
    )
    return df


def test_create_column():
    """
    CreateColumn:
        column_name: C
        value: 7
    """
    config = get_pipeline_config(yaml_path=YAML_PATH)

    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    assert 'C' in df.columns
    assert df['C'].unique()[0] == 7


def test_dropna():
    """
    DropNA:
        column_name: NA_col
    """
    config = get_pipeline_config(yaml_path=YAML_PATH)

    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    assert np.nan not in df['NA_col']


def test_fill_column():
    """
    FillColumn:
        column_name: B
        value: 0
    """
    config = get_pipeline_config(yaml_path=YAML_PATH)
    
    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    assert np.nan not in df['B']
    assert 0 in df['B']


def test_filter_rows():
    """
    FilterRows:
        first_column: A
        second_column: B
        logic: le
    """
    config = get_pipeline_config(yaml_path=YAML_PATH)
    
    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    res = df.loc[
        df['A'] <= df['B']
    ]

    assert df.equals(res)


def test_merge_dataframes():
    """
    MergeDataFrames:
        df_to_join: df_2
        join_cols: ['A']
        how: inner
        suffixes: ['_1', '_2']
    """
    config = get_pipeline_config(yaml_path=YAML_PATH)

    df = generate_mock_df()
    second_df = generate_mock_df()
    df = run_pipeline(df, config=config, extra_dfs={'df_2': second_df})

    assert 'B_1' in df.columns
    assert 'B_2' in df.columns


def test_multiply_columns():
    """
    MultiplyColumns:
        first_column: A
        second_column: B
        resulting_column: mul
    """
    config = get_pipeline_config(yaml_path=YAML_PATH)

    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    assert 'mul' in df.columns
    assert (df['A'] * df['B']).equals(df['mul'])


def test_normalize_column():
    """
    NormalizeColumn:
        column_name: A
        output_column: A_norm
    """
    config = get_pipeline_config(yaml_path=YAML_PATH)

    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    assert 'A_norm' in df.columns
    assert ((df['A'] - df['A'].mean()) / df['A'].std()).equals(df['A_norm'])


def test_remove_column():
    """
    RemoveColumn:
        column_name: ToRemove
    """
    config = get_pipeline_config(yaml_path=YAML_PATH)
    
    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    assert 'ToRemove' not in df.columns


def test_rename_column():
    """
    RenameColumn:
        old_column_name: ToRename
        new_columnName: RenamedColumn
    """
    config = get_pipeline_config(yaml_path=YAML_PATH)
    
    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    assert 'ToRename' not in df.columns
    assert 'RenamedColumn' in df.columns
