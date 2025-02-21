# pytest -s -v

import pandas as pd
from src.pipeline_loader import get_pipeline_config, run_pipeline

def generate_mock_df():
    df = pd.DataFrame(
        {
            'A': [1, 2, 3],
            'B': [4, 5, 6]
        }
    )
    return df

def test_create_column():
    """
    CreateColumn:
        column_name: C
        value: 7
    """
    df = generate_mock_df()
    config = get_pipeline_config(yaml_path='tests/test_pipeline.yaml')
    df = run_pipeline(df, config=config)

    assert 'C' in df.columns
    assert df['C'].unique()[0] == 7


def test_multiply_columns():
    """
    MultiplyColumns:
        first_column: A
        second_column: B
        resulting_column: mul
    """
    df = generate_mock_df()
    config = get_pipeline_config(yaml_path='tests/test_pipeline.yaml')
    df = run_pipeline(df, config=config)

    assert 'mul' in df.columns
    assert (df['A'] * df['B']).equals(df['mul'])


def test_normalize_column():
    """
    NormalizeColumn:
        column_name: A
        output_column: A_norm
    """
    df = generate_mock_df()
    config = get_pipeline_config(yaml_path='tests/test_pipeline.yaml')
    df = run_pipeline(df, config=config)

    assert 'A_norm' in df.columns
    assert ((df['A'] - df['A'].mean()) / df['A'].std()).equals(df['A_norm'])
