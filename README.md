# ⚙️ DataMorphers

![Unit Tests](https://github.com/davideganna/DataMorph/actions/workflows/tests.yaml/badge.svg)
[![codecov](https://codecov.io/gh/davideganna/DataMorphers/graph/badge.svg?token=MXTUZEDC44)](https://codecov.io/gh/davideganna/DataMorphers)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)
![PyPI version](https://img.shields.io/pypi/v/datamorphers.svg)

<p align="center">
  <img src="https://github.com/user-attachments/assets/f1b01b79-4032-4688-82a1-c586a7ee9f9a" width=420>
</p>

## Overview

DataMorphers is a Python library that provides a flexible framework for transforming Pandas DataFrames using a modular data pipeline approach. Transformations are defined in a YAML configuration, and are applied sequentially to your dataset.

By leveraging DataMorphers, your pipelines become cleaner, more scalable and easier to debug.

## Features

- Modular and extensible transformation framework.
- Easily configurable via YAML files.
- Supports multiple transformations, alphabetically ordered here (more to come!):
  - [CreateColumn](https://github.com/davideganna/DataMorphers/blob/4a8ee2e513793224876f721f22fdb1a08097ce05/datamorphers/datamorphers.py#L7)
  - [CastColumnTypes](https://github.com/davideganna/DataMorphers/blob/4a8ee2e513793224876f721f22fdb1a08097ce05/datamorphers/datamorphers.py#L19)
  - [ColumnsOperator](https://github.com/davideganna/DataMorphers/blob/4a8ee2e513793224876f721f22fdb1a08097ce05/datamorphers/datamorphers.py#L30)
  - [DeleteDataFrame](https://github.com/davideganna/DataMorphers/blob/4a8ee2e513793224876f721f22fdb1a08097ce05/datamorphers/datamorphers.py#L58)
  - [DropNA](https://github.com/davideganna/DataMorphers/blob/4a8ee2e513793224876f721f22fdb1a08097ce05/datamorphers/datamorphers.py#L76)
  - [FillNA](https://github.com/davideganna/DataMorphers/blob/4a8ee2e513793224876f721f22fdb1a08097ce05/datamorphers/datamorphers.py#L87)
  - [FilterRows](https://github.com/davideganna/DataMorphers/blob/4a8ee2e513793224876f721f22fdb1a08097ce05/datamorphers/datamorphers.py#L99)
  - [FlatMultiIndex](https://github.com/davideganna/DataMorphers/blob/4a8ee2e513793224876f721f22fdb1a08097ce05/datamorphers/datamorphers.py#L122)
  - [MathOperator](https://github.com/davideganna/DataMorphers/blob/4a8ee2e513793224876f721f22fdb1a08097ce05/datamorphers/datamorphers.py#L142)
  - [MergeDataFrames](https://github.com/davideganna/DataMorphers/blob/4a8ee2e513793224876f721f22fdb1a08097ce05/datamorphers/datamorphers.py#L164)
  - [NormalizeColumn](https://github.com/davideganna/DataMorphers/blob/4a8ee2e513793224876f721f22fdb1a08097ce05/datamorphers/datamorphers.py#L185)
  - [RemoveColumns](https://github.com/davideganna/DataMorphers/blob/4a8ee2e513793224876f721f22fdb1a08097ce05/datamorphers/datamorphers.py#L199)
  - [RenameColumn](https://github.com/davideganna/DataMorphers/blob/4a8ee2e513793224876f721f22fdb1a08097ce05/datamorphers/datamorphers.py#L212)
  - [SaveDataFrame](https://github.com/davideganna/DataMorphers/blob/4a8ee2e513793224876f721f22fdb1a08097ce05/datamorphers/datamorphers.py#L224)
  - [SelectColumns](https://github.com/davideganna/DataMorphers/blob/4a8ee2e513793224876f721f22fdb1a08097ce05/datamorphers/datamorphers.py#L240)
- Supports custom transformations, defined by the user.

## Installation

Install DataMorphers in your project directly from PyPI:

```sh
pip install datamorphers
```

## Usage

### 1. Define your initial DataFrame

```python
import pandas as pd

# Sample DataFrame
df = pd.DataFrame(
  {
      'item': ['apple', 'TV', 'banana', 'pasta', 'cake'],
      'item_type': ['food', 'electronics', 'food', 'food', 'food'],
      'price': [3, 100, 2.5, 3, 15],
      'discount_pct': [0.1, 0.05, np.nan, 0.12, np.nan],
  }
)
```

| item   | item_type   |   price |   discount_pct |
|:-------|:------------|--------:|---------------:|
| apple  | food        |     3   |           0.1  |
| TV     | electronics |   100   |           0.05 |
| banana | food        |     2.5 |         nan    |
| pasta  | food        |     3   |           0.12 |
| cake   | food        |    15   |         nan    |

### 2. Define Your Transformation Pipeline

Imagine that we want to perform some actions on the original DataFrame.
Specifically, we want to identify which items are food, and then calculate the price after a discount percentage is applied. After these operations, we want to polish the DataFrame by removing non interesting columns.

To do so, we create a YAML file specifying a pipeline of transformations, named `config.yaml`:

```yaml
pipeline_food:
  # Create a column named "food_marker", containing a fixed value named "food".
  - CreateColumn:
      column_name: food_marker
      value: food

  # Compare the columns "item_type" and "food_marker", and keep rows that are equal (logic: "e").
  - FilterRows:
      first_column: item_type
      second_column: food_marker
      logic: e

  # Some values in the column "discount_pct" are NaN. Fill them with 0.
  - FillNA:
      column_name: discount_pct
      value: 0

  # Multiply the columns "price" and "discount_pct". Name the output column "discount_amount".
  - ColumnsOperator:
      first_column: price
      second_column: discount_pct
      logic: mul
      output_column: discount_amount

  # Subtract the columns "price" and "discount_amount". Name the output column "discounted_price".
  - ColumnsOperator:
      first_column: price
      second_column: discount_amount
      logic: sub
      output_column: discounted_price

  # Remove non interesting columns from the DataFrame.
  - RemoveColumns:
      columns_name:
        - discount_amount
        - food_marker
```

### 3. Apply the transformations as defined in the config

Running the pipeline is very simple:

```python
from datamorphers.pipeline_loader import get_pipeline_config, run_pipeline

# Load YAML config
config = get_pipeline_config("config.yaml", pipeline_name='pipeline_food'))

# Run pipeline
transformed_df = run_pipeline(df, config)
```
A log visually shows your data pipeline:
```plaintext
- INFO - Loading pipeline named: pipeline_food
- INFO - *** DataMorpher: CreateColumn ***
- INFO -     column_name: food_marker
- INFO -     value: food
- INFO - *** DataMorpher: FilterRows ***
- INFO -     first_column: item_type
- INFO -     second_column: food_marker
- INFO -     logic: e
- INFO - *** DataMorpher: FillNA ***
- INFO -     column_name: discount_pct
- INFO -     value: 0
- INFO - *** DataMorpher: ColumnsOperator ***
- INFO -     first_column: price
- INFO -     second_column: discount_pct
- INFO -     logic: mul
- INFO -     output_column: discount_amount
- INFO - *** DataMorpher: ColumnsOperator ***
- INFO -     first_column: price
- INFO -     second_column: discount_amount
- INFO -     logic: sub
- INFO -     output_column: discounted_price
- INFO - *** DataMorpher: RemoveColumns ***
- INFO -     columns_name: ['discount_amount', 'food_marker']
```
The resulting DataFrame follows:
| item   | item_type   |   price |   discount_pct |   discounted_price |
|:-------|:------------|--------:|---------------:|-------------------:|
| apple  | food        |     3   |           0.1  |               2.7  |
| banana | food        |     2.5 |           0    |               2.5  |
| pasta  | food        |     3   |           0.12 |               2.64 |
| cake   | food        |    15   |           0    |              15    |

---

## Define runtime values in the YAML configuration

DataMorph can work with variables evaluated at runtime, making it very flexible:

```yaml
pipeline_runtime:
  - CreateColumn:
      column_name: ${custom_column_name}
      value: ${custom_value}
```

Simply pass the arguments you need when you instantiate the pipeline:

```python
custom_column_name = "D"
custom_value = 888

kwargs = {
  "custom_column_name": custom_column_name,
  "custom_value": custom_value
}

config = get_pipeline_config(
    yaml_path=YAML_PATH,
    pipeline_name="pipeline_runtime",
    **kwargs,
)

df = run_pipeline(df, config=config)
```

---

## Extending `datamorphers` with Custom Implementations

Limiting the pipelines to only the basic DataMorphers defined in this library would make this package of little use.
For this reason, `datamorphers` allows you to define custom transformations by implementing your own DataMorphers. These user-defined implementations extend the base ones and can be used seamlessly within the pipeline.

### Creating a Custom DataMorpher

To define a custom transformation, create a `custom_datamorphers.py` file in your project and implement a new class that follows the `DataMorpher` structure:

```python
import pandas as pd
import numpy as np
from datamorphers.base import DataMorpher

class CalculateCircularArea(DataMorpher):
    def __init__(self, radius_column: str, output_column: str):
        self.radius_column = radius_column
        self.output_column = output_column

    def _datamorph(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates the area of a circle.
        """
        df[self.output_column] = np.pi * df[self.radius_column] ** 2
        return df
```

### Importing Custom DataMorphers

To use your custom implementations, create a file named `custom_datamorphers.py` inside your current directory.

The pipeline will first check for the specified DataMorpher in `custom_datamorphers`. If it's not found, it will fall back to the default ones in `datamorphers`. This allows for seamless extension without modifying the base package.


### Running the Pipeline with Custom DataMorphers

When defining a pipeline configuration in the YAML file, simply reference your custom DataMorpher as you would with a base one:

```yaml
custom_pipeline:
  - CalculateCircularArea:
      radius_column: radius
      output_column: area_circle
```

Then, execute the pipeline as usual:

```python
df_transformed = run_pipeline(df, config)
```

If a custom module is provided, your custom transformations will be used instead of (or in addition to) the built-in ones.

---

## Pre-commit Hooks

To ensure code quality, install and configure pre-commit hooks:

```sh
pre-commit install
pre-commit run --all-files
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

MIT License. See `LICENSE` for details.
