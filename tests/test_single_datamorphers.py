# pytest -s -v --disable-pytest-warnings

import logging

import narwhals as nw
import numpy as np
import pandas as pd

from datamorphers.pipeline_loader import get_pipeline_config, run_pipeline

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
            "A": [1, 2, 2, 2, 3],
            "B": [4, 5, 5, 6, np.nan],
            "C": [7, 8, 8, 8.5, 9],
            "D": ["WHITE", "black", "OrAnge", "BROWN", "green"],
            "E": ["red", "Blue", "YelloW", "LIGHT_BLUE", "PInk"],
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

    df: pd.DataFrame = run_pipeline(df, config=config)

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
    df["Date"] = df.shape[0] * ["01-01-2000"]
    df["DateTime"] = df.shape[0] * ["01-01-2000 00:00:00"]
    df = nw.from_native(run_pipeline(df, config=config))

    assert isinstance(df["A"].dtype, nw.Float32)
    assert isinstance(df["C"].dtype, nw.String)
    assert isinstance(df["Date"].dtype, nw.Date)
    assert isinstance(df["DateTime"].dtype, nw.Datetime)


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
    df: pd.DataFrame = run_pipeline(df, config=config)

    res_sum = df["A"] + df["B"]
    res_sub = df["A"] - df["B"]
    res_mul = df["A"] * df["B"]
    res_div = df["A"] / df["B"]

    assert (df["A_sum_B"]).equals(res_sum)
    assert (df["A_sub_B"]).equals(res_sub)
    assert (df["A_mul_B"]).equals(res_mul)
    assert (df["A_div_B"]).equals(res_div)


def test_drop_duplicates():
    def _test_drop_duplicates_all():
        """
        - DropDuplicates
        """
        config = get_pipeline_config(
            yaml_path=YAML_PATH, pipeline_name="pipeline_DropDuplicates_all"
        )

        df = generate_mock_df()
        df_out = run_pipeline(df, config=config)

        df_no_dup = df.drop_duplicates()

        assert df_out.equals(df_no_dup)

    def _test_drop_duplicates_subset_single():
        """
        - DropDuplicates
            subset: A
        """
        config = get_pipeline_config(
            yaml_path=YAML_PATH, pipeline_name="pipeline_DropDuplicates_subset_single"
        )

        df = generate_mock_df()
        df_out = run_pipeline(df, config=config)

        df_no_dup = df.drop_duplicates(subset="A")

        assert df_out.equals(df_no_dup)

    def _test_drop_duplicates_subset_list():
        """
        - DropDuplicates
            subset: A
        """
        config = get_pipeline_config(
            yaml_path=YAML_PATH, pipeline_name="pipeline_DropDuplicates_subset_list"
        )

        df = generate_mock_df()
        df_out = run_pipeline(df, config=config)

        df_no_dup = df.drop_duplicates(subset=["A"])

        assert df_out.equals(df_no_dup)

    _test_drop_duplicates_all()
    _test_drop_duplicates_subset_single()
    _test_drop_duplicates_subset_list()


def test_dropna():
    """
    - DropNA:
        column_name: B
    """
    config = get_pipeline_config(yaml_path=YAML_PATH, pipeline_name="pipeline_DropNA")

    df = generate_mock_df()
    df: pd.DataFrame = run_pipeline(df, config=config)

    assert np.nan not in df["B"]


def test_fillna():
    """
    - FillNA:
        column_name: B
        value: 0
    """
    config = get_pipeline_config(yaml_path=YAML_PATH, pipeline_name="pipeline_FillNA")

    df = generate_mock_df()
    df: pd.DataFrame = run_pipeline(df, config=config)

    assert np.nan not in df["B"]
    assert 0 in df["B"]


def test_filter_rows():
    def _test_filter_rows_e():
        """
        - FilterRows:
            first_column: A
            second_column: true
            logic: eq
        """
        config = get_pipeline_config(
            yaml_path=YAML_PATH, pipeline_name="pipeline_FilterRows_e"
        )

        df = generate_mock_df()
        df: pd.DataFrame = run_pipeline(df, config=config)

        res = df.loc[df["A"] == True]

        assert df.equals(res)

    def _test_filter_rows_gt():
        """
        - FilterRows:
            first_column: A
            second_column: 3.14
            logic: g
        """
        config = get_pipeline_config(
            yaml_path=YAML_PATH, pipeline_name="pipeline_FilterRows_gt"
        )

        df = generate_mock_df()
        df: pd.DataFrame = run_pipeline(df, config=config)

        res = df.loc[df["A"] > 3.14]

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
        df: pd.DataFrame = run_pipeline(df, config=config)

        res = df.loc[df["A"] >= df["B"]]
        assert df.equals(res)

    def _test_filter_rows_lt():
        """
        - FilterRows:
            first_column: A
            second_column: B
            logic: l
        """
        config = get_pipeline_config(
            yaml_path=YAML_PATH, pipeline_name="pipeline_FilterRows_lt"
        )

        df = generate_mock_df()
        df: pd.DataFrame = run_pipeline(df, config=config)

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
        df: pd.DataFrame = run_pipeline(df, config=config)

        res = df.loc[df["A"] <= df["B"]]

        assert df.equals(res)

    _test_filter_rows_e()
    _test_filter_rows_gt()
    _test_filter_rows_ge()
    _test_filter_rows_lt()
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
    df: pd.DataFrame = run_pipeline(df, config=config)

    assert df.columns.equals(pd.Index(["A_B", "C_D", "E"]))


def test_merge_dataframes():
    """
    - MergeDataFrames:
        df_to_join: ${second_df}
        join_cols: ['A', 'B']
        how: inner
        suffix: '1'
    """
    df = generate_mock_df()
    second_df = generate_mock_df()
    kwargs = {"second_df": second_df}

    config = get_pipeline_config(
        yaml_path=YAML_PATH, pipeline_name="pipeline_MergeDataFrames", **kwargs
    )

    df: pd.DataFrame = run_pipeline(df, config=config)

    assert "C" in df.columns
    assert "C1" in df.columns


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
    df: pd.DataFrame = run_pipeline(df, config=config)

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
    df: pd.DataFrame = run_pipeline(df, config=config)

    assert "A" not in df.columns
    assert "B" not in df.columns
    assert "C" not in df.columns


def test_rename_columns():
    """
    - RenameColumns:
        cols_mapping:
            A: A_remapped
            B: B_remapped
    """
    config = get_pipeline_config(
        yaml_path=YAML_PATH, pipeline_name="pipeline_RenameColumns"
    )

    df = generate_mock_df()
    df: pd.DataFrame = run_pipeline(df, config=config)

    assert "A" not in df.columns
    assert "B" not in df.columns
    assert "A_remapped" in df.columns
    assert "B_remapped" in df.columns


def test_rolling():
    """
    - Rolling:
        column_name: A
        how: mean
        window_size: 2
        output_column: rolling_mean

    - Rolling:
        column_name: A
        how: std
        window_size: 2
        output_column: rolling_std

    - Rolling:
        column_name: A
        how: sum
        window_size: 2
        output_column: rolling_sum

    - Rolling:
        column_name: A
        how: var
        window_size: 2
        output_column: rolling_var
    """
    config = get_pipeline_config(yaml_path=YAML_PATH, pipeline_name="pipeline_Rolling")

    df = generate_mock_df()
    df: pd.DataFrame = run_pipeline(df, config=config)

    rolling_mean = df["A"].rolling(2).mean()
    rolling_std = df["A"].rolling(2).std()
    rolling_sum = df["A"].rolling(2).sum()
    rolling_var = df["A"].rolling(2).var()

    assert df["rolling_mean"].equals(rolling_mean)
    assert df["rolling_std"].equals(rolling_std)
    assert df["rolling_sum"].equals(rolling_sum)
    assert df["rolling_var"].equals(rolling_var)


def test_select_columns():
    """
    - SelectColumns:
        columns: [A, B]
    """
    config = get_pipeline_config(
        yaml_path=YAML_PATH, pipeline_name="pipeline_SelectColumns"
    )

    df = generate_mock_df()
    df: pd.DataFrame = run_pipeline(df, config=config)

    assert "A" in df.columns
    assert "B" in df.columns
    assert "C" not in df.columns


def test_to_lower():
    """
    - ToLower:
        columns: D
    """
    config = get_pipeline_config(yaml_path=YAML_PATH, pipeline_name="pipeline_ToLower")

    df: pd.DataFrame = generate_mock_df()
    df = run_pipeline(df, config=config)

    assert df["D"].equals(df["D"].str.lower())


def test_to_upper():
    """
    - ToLower:
        columns: [D, E]
    """
    config = get_pipeline_config(yaml_path=YAML_PATH, pipeline_name="pipeline_ToUpper")

    df: pd.DataFrame = generate_mock_df()
    df = run_pipeline(df, config=config)

    assert df["D"].equals(df["D"].str.upper())
    assert df["E"].equals(df["E"].str.upper())
