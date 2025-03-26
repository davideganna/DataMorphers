# pytest -s -v --disable-pytest-warnings

import pandas as pd
import numpy as np
from datamorphers.pipeline_loader import get_pipeline_config, run_pipeline

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True,
)

logger = logging.getLogger(__name__)

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


def test_create_dynamic_column():
    """
    Creates a column with a dynamic name and value.

    - CreateColumn:
        column_name: ${custom_column_name}
        value: ${custom_value}
    """
    df = generate_mock_df()

    custom_column_name = "D"
    custom_value = 888

    kwargs = {"custom_column_name": custom_column_name, "custom_value": custom_value}

    config = get_pipeline_config(
        yaml_path=YAML_PATH,
        pipeline_name="pipeline_CreateColumn",
        **kwargs,
    )

    df = run_pipeline(df, config=config)

    assert "D" in df.columns
    assert df["D"].unique()[0] == 888


def test_cast_columns_type():
    """
    pipeline_CastColumnTypes:
        - CastColumnTypes:
            cast_dict:
                A: float16
                C: str
    """
    config = get_pipeline_config(
        yaml_path=YAML_PATH, pipeline_name="pipeline_CastColumnTypes"
    )

    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    assert isinstance(df["A"].dtype, type(np.dtype("float16")))
    assert isinstance(df["C"].dtype, type(np.dtype("object")))


def test_columns_operator():
    """
    - ColumnsOperator:
      first_column: A
      second_column: B
      logic: sum
      output_column: A_sum_B

    - ColumnsOperator:
        first_column: A
        second_column: B
        logic: sub
        output_column: A_sub_B

    - ColumnsOperator:
        first_column: A
        second_column: B
        logic: mul
        output_column: A_mul_B

    - ColumnsOperator:
        first_column: A
        second_column: B
        logic: div
        output_column: A_div_B
    """
    config = get_pipeline_config(
        yaml_path=YAML_PATH, pipeline_name="pipeline_ColumnsOperator"
    )

    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    res_sum = df["A"] + df["B"]
    res_sub = df["A"] - df["B"]
    res_mul = df["A"] * df["B"]
    res_div = df["A"] / df["B"]

    assert (df["A_sum_B"]).equals(res_sum)
    assert (df["A_sub_B"]).equals(res_sub)
    assert (df["A_mul_B"]).equals(res_mul)
    assert (df["A_div_B"]).equals(res_div)


def test_dropna():
    """
    - DropNA:
        column_name: B
    """
    config = get_pipeline_config(yaml_path=YAML_PATH, pipeline_name="pipeline_DropNA")

    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    assert np.nan not in df["B"]


def test_fillna():
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
    def _test_filter_rows_e():
        """
        - FilterRows:
            first_column: A
            second_column: B
            logic: e
        """
        config = get_pipeline_config(
            yaml_path=YAML_PATH, pipeline_name="pipeline_FilterRows_e"
        )

        df = generate_mock_df()
        df = run_pipeline(df, config=config)

        res = df.loc[df["A"] == df["B"]]

        assert df.equals(res)

    def _test_filter_rows_g():
        """
        - FilterRows:
            first_column: A
            second_column: B
            logic: g
        """
        config = get_pipeline_config(
            yaml_path=YAML_PATH, pipeline_name="pipeline_FilterRows_g"
        )

        df = generate_mock_df()
        df = run_pipeline(df, config=config)

        res = df.loc[df["A"] > df["B"]]

        assert df.equals(res)

    def _test_filter_rows_ge():
        """
        - FilterRows:
            first_column: A
            second_column: B
            logic: ge
        """
        config = get_pipeline_config(
            yaml_path=YAML_PATH, pipeline_name="pipeline_FilterRows_ge"
        )

        df = generate_mock_df()
        df = run_pipeline(df, config=config)

        res = df.loc[df["A"] >= df["B"]]

        assert df.equals(res)

    def _test_filter_rows_l():
        """
        - FilterRows:
            first_column: A
            second_column: B
            logic: l
        """
        config = get_pipeline_config(
            yaml_path=YAML_PATH, pipeline_name="pipeline_FilterRows_l"
        )

        df = generate_mock_df()
        df = run_pipeline(df, config=config)

        res = df.loc[df["A"] < df["B"]]

        assert df.equals(res)

    def _test_filter_rows_le():
        """
        - FilterRows:
            first_column: A
            second_column: B
            logic: le
        """
        config = get_pipeline_config(
            yaml_path=YAML_PATH, pipeline_name="pipeline_FilterRows_le"
        )

        df = generate_mock_df()
        df = run_pipeline(df, config=config)

        res = df.loc[df["A"] <= df["B"]]

        assert df.equals(res)

    _test_filter_rows_e()
    _test_filter_rows_g()
    _test_filter_rows_ge()
    _test_filter_rows_l()
    _test_filter_rows_le()


def test_flat_multi_index():
    """
    - FlatMultiIndex:
    """
    config = get_pipeline_config(
        yaml_path=YAML_PATH, pipeline_name="pipeline_FlatMultiIndex"
    )

    df = pd.DataFrame(
        {
            ("A", "B"): [1, 2, 3],
            ("C", "D"): [4, 5, 6],
            "E": [7, 8, 9],
        }
    )
    df = run_pipeline(df, config=config)

    assert df.columns.equals(pd.Index(["A_B", "C_D", "E"]))


def test_math_operator():
    """
    - MathOperator:
      column_name: A
      logic: sum
      value: 3
      output_column: sum_col

    - MathOperator:
        column_name: A
        logic: sub
        value: 3
        output_column: sub_col

    - MathOperator:
        column_name: A
        logic: mul
        value: 3
        output_column: mul_col

    - MathOperator:
        column_name: A
        logic: div
        value: 3
        output_column: div_col
    """
    config = get_pipeline_config(
        yaml_path=YAML_PATH, pipeline_name="pipeline_MathOperator"
    )

    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    res_sum = df["A"] + 3
    res_sub = df["A"] - 3
    res_mul = df["A"] * 3
    res_div = df["A"] / 3

    assert df["sum_col"].equals(res_sum)
    assert df["sub_col"].equals(res_sub)
    assert df["mul_col"].equals(res_mul)
    assert df["div_col"].equals(res_div)


def test_merge_dataframes():
    """
    - MergeDataFrames:
        df_to_join: ${second_df}
        join_cols: ['A', 'B']
        how: inner
        suffixes: ['_1', '_2']
    """
    df = generate_mock_df()
    second_df = generate_mock_df()
    kwargs = {"second_df": second_df}

    config = get_pipeline_config(
        yaml_path=YAML_PATH, pipeline_name="pipeline_MergeDataFrames", **kwargs
    )

    df = run_pipeline(df, config=config)

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


def test_select_columns():
    """
    - SelectColumns:
        columns: [A, B]
    """
    config = get_pipeline_config(
        yaml_path=YAML_PATH, pipeline_name="pipeline_SelectColumns"
    )

    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    assert "A" in df.columns
    assert "B" in df.columns
    assert "C" not in df.columns


# Keep it last: deletes a DataFrame saved using 'SaveDataFrame'
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
