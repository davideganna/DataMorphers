# pytest -s -v --disable-pytest-warnings

import pandas as pd
import numpy as np
from datamorphers.pipeline_loader import get_pipeline_config, run_pipeline

YAML_PATH = "tests/pipelines/test_single_datamorphers.yaml"


def generate_mock_df():
    df = pd.DataFrame(
        {
            "A": [1, 2, 3],
            "B": [4, 5, np.nan],
            "C": [7, 8, 9],
        }
    )
    return df


def test_add_column():
    """
    - AddColumn:
        column_name: D
        value: 999
    """
    config = get_pipeline_config(
        yaml_path=YAML_PATH, pipeline_name="pipeline_AddColumn"
    )

    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    assert "D" in df.columns
    assert df["D"].unique()[0] == 999


def test_columns_operator():
    """
    - ColumnsOperator:
        first_column: A
        second_column: B
        logic: mul
        output_column: A_x_B

    - ColumnsOperator:
        first_column: A
        second_column: B
        logic: sub
        output_column: A_minus_B
    """
    config = get_pipeline_config(
        yaml_path=YAML_PATH, pipeline_name="pipeline_ColumnsOperator"
    )

    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    res_mul = df["A"] * df["B"]
    res_sub = df["A"] - df["B"]

    assert (df["A_x_B"]).equals(res_mul)
    assert (df["A_minus_B"]).equals(res_sub)


def test_dropna():
    """
    - DropNA:
        column_name: B
    """
    config = get_pipeline_config(yaml_path=YAML_PATH, pipeline_name="pipeline_DropNA")

    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    assert np.nan not in df["B"]


def test_FillNA():
    """
    - FillNA:
        column_name: B
        value: 0
    """
    config = get_pipeline_config(yaml_path=YAML_PATH, pipeline_name="pipeline_FillNA")

    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    assert np.nan not in df["B"]
    assert 0 in df["B"]


def test_filter_rows():
    """
    - FilterRows:
        first_column: A
        second_column: B
        logic: le
    """
    config = get_pipeline_config(
        yaml_path=YAML_PATH, pipeline_name="pipeline_FilterRows"
    )

    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    res = df.loc[df["A"] <= df["B"]]

    assert df.equals(res)


def test_math_operator():
    """
    - MathOperator:
        column_name: A
        logic: div
        value: 3
        output_column: div_col

    - MathOperator:
        column_name: A
        logic: sum
        value: 3
        output_column: sum_col
    """
    config = get_pipeline_config(
        yaml_path=YAML_PATH, pipeline_name="pipeline_MathOperator"
    )

    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    res_div = df["A"] / 3
    res_sum = df["A"] + 3

    assert df["div_col"].equals(res_div)
    assert df["sum_col"].equals(res_sum)


def test_merge_dataframes():
    """
    - MergeDataFrames:
        df_to_join: df_2
        join_cols: ['A', 'B']
        how: inner
        suffixes: ['_1', '_2']
    """
    config = get_pipeline_config(
        yaml_path=YAML_PATH, pipeline_name="pipeline_MergeDataFrames"
    )

    df = generate_mock_df()
    second_df = generate_mock_df()
    df = run_pipeline(df, config=config, extra_dfs={"df_2": second_df})

    assert "C_1" in df.columns
    assert "C_2" in df.columns


def test_normalize_column():
    """
    - NormalizeColumn:
        column_name: A
        output_column: A_norm
    """
    config = get_pipeline_config(
        yaml_path=YAML_PATH, pipeline_name="pipeline_NormalizeColumn"
    )

    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    assert "A_norm" in df.columns
    assert ((df["A"] - df["A"].mean()) / df["A"].std()).equals(df["A_norm"])


def test_remove_columns():
    """
      - RemoveColumns:
        columns_name: A
    - RemoveColumns:
        columns_name: [
          B,
          C
        ]
    """
    config = get_pipeline_config(
        yaml_path=YAML_PATH, pipeline_name="pipeline_RemoveColumns"
    )

    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    assert "A" not in df.columns
    assert "B" not in df.columns
    assert "C" not in df.columns


def test_rename_column():
    """
    - RenameColumn:
        old_column_name: ToRename
        new_columnName: RenamedColumn
    """
    config = get_pipeline_config(
        yaml_path=YAML_PATH, pipeline_name="pipeline_RenameColumn"
    )

    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    assert "A" not in df.columns
    assert "RenamedColumn" in df.columns


def test_save_dataframe():
    """
    - SaveDataFrame:
        file_name: saved_df
    """
    import os.path

    config = get_pipeline_config(
        yaml_path=YAML_PATH, pipeline_name="pipeline_SaveDataFrame"
    )

    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    assert os.path.isfile("saved_df.pkl")


def test_delete_dataframe():
    """
    - DeleteDataFrame:
        file_name: saved_df
    """
    import os

    config = get_pipeline_config(
        yaml_path=YAML_PATH, pipeline_name="pipeline_DeleteDataFrame"
    )

    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    assert "saved_df.pkl" not in os.listdir()
