# pytest -s -v --disable-pytest-warnings

import numpy as np
import pandas as pd

from datamorphers.pipeline_loader import get_pipeline_config, run_pipeline

YAML_PATH = "tests/pipelines/test_pipeline.yaml"


def generate_mock_df():
    df = pd.DataFrame(
        {
            "item": ["apple", "TV", "banana", "pasta", "cake"],
            "item_type": ["food", "electronics", "food", "food", "food"],
            "price": [3, 100, 2.5, 3, 15],
            "discount_pct": [0.1, 0.05, np.nan, 0.12, np.nan],
        }
    )
    return df


def test_pipeline():
    """
    - FilterRows:
        first_column: item_type
        second_column: food_marker
        logic: e

    - FillNA:
        column_name: discount_pct
        value: 0

    - ColumnsOperator:
        first_column: price
        second_column: discount_pct
        logic: mul
        output_column: discount_amount

    - ColumnsOperator:
        first_column: price
        second_column: discount_amount
        logic: sub
        output_column: discounted_price

    - RemoveColumns:
        columns_name:
            - discount_amount
    """
    config = get_pipeline_config(yaml_path=YAML_PATH, pipeline_name="pipeline_food")

    df = generate_mock_df()
    df = run_pipeline(df, config=config)

    res_df = pd.DataFrame(
        {
            "item": {0: "apple", 2: "banana", 3: "pasta", 4: "cake"},
            "item_type": {0: "food", 2: "food", 3: "food", 4: "food"},
            "price": {0: 3.0, 2: 2.5, 3: 3.0, 4: 15.0},
            "discount_pct": {0: 0.1, 2: 0.0, 3: 0.12, 4: 0.0},
            "discounted_price": {0: 2.7, 2: 2.5, 3: 2.64, 4: 15.0},
        }
    )

    assert df.equals(res_df)
