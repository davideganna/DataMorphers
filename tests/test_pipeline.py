# pytest -s -v --disable-pytest-warnings

import pandas as pd
import numpy as np
from datamorphers.pipeline_loader import get_pipeline_config, run_pipeline

YAML_PATH = 'tests/test_pipeline.yaml'

def generate_mock_df():
    df = pd.DataFrame(
        {
            'A': [1, 2, 3],
            'B': [4, 5, np.nan],
            'C': [7, 8, 9],
        }
    )
    return df


def test_create_column():
    """
    CreateColumn:
        column_name: D
        value: 999
    """
    config = get_pipeline_config(yaml_path=YAML_PATH, pipeline_name='pipeline_CreateColumn')

    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    assert 'D' in df.columns
    assert df['D'].unique()[0] == 999


def test_dropna():
    """
    DropNA:
        column_name: B
    """
    config = get_pipeline_config(yaml_path=YAML_PATH, pipeline_name='pipeline_DropNA')

    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    assert np.nan not in df['B']


def test_fill_column():
    """
    FillColumn:
        column_name: B
        value: 0
    """
    config = get_pipeline_config(yaml_path=YAML_PATH, pipeline_name='pipeline_FillColumn')

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
    config = get_pipeline_config(yaml_path=YAML_PATH, pipeline_name='pipeline_FilterRows')

    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    res = df.loc[
        df['A'] <= df['B']
    ]

    assert df.equals(res)


def test_math_operator():
    """
    MathOperator:
        column_name: A
        logic: div
        value: 3
        output_column: div_col

    MathOperator:
        column_name: A
        logic: sum
        value: 3
        output_column: sum_col
    """
    config = get_pipeline_config(yaml_path=YAML_PATH, pipeline_name='pipeline_MathOperator')

    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    res_div = df['A'] / 3
    res_sum = df['A'] + 3

    assert df['div_col'].equals(res_div)
    assert df['sum_col'].equals(res_sum)



def test_merge_dataframes():
    """
    MergeDataFrames:
        df_to_join: df_2
        join_cols: ['A', 'B']
        how: inner
        suffixes: ['_1', '_2']
    """
    config = get_pipeline_config(yaml_path=YAML_PATH, pipeline_name='pipeline_MergeDataFrames')

    df = generate_mock_df()
    second_df = generate_mock_df()
    df = run_pipeline(df, config=config, extra_dfs={'df_2': second_df})

    assert 'C_1' in df.columns
    assert 'C_2' in df.columns


def test_multiply_columns():
    """
    MultiplyColumns:
        first_column: A
        second_column: B
        resulting_column: mul
    """
    config = get_pipeline_config(yaml_path=YAML_PATH, pipeline_name='pipeline_MultiplyColumns')

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
    config = get_pipeline_config(yaml_path=YAML_PATH, pipeline_name='pipeline_NormalizeColumn')

    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    assert 'A_norm' in df.columns
    assert ((df['A'] - df['A'].mean()) / df['A'].std()).equals(df['A_norm'])


def test_remove_column():
    """
    RemoveColumn:
        column_name: A
    """
    config = get_pipeline_config(yaml_path=YAML_PATH, pipeline_name='pipeline_RemoveColumn')

    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    assert 'A' not in df.columns


def test_rename_column():
    """
    RenameColumn:
        old_column_name: ToRename
        new_columnName: RenamedColumn
    """
    config = get_pipeline_config(yaml_path=YAML_PATH, pipeline_name='pipeline_RenameColumn')

    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    assert 'A' not in df.columns
    assert 'RenamedColumn' in df.columns
