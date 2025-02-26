# ⚙️ DataMorph

![Unit Tests](https://github.com/davideganna/DataMorph/actions/workflows/tests.yaml/badge.svg)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)


## Overview

DataMorph is a Python library that provides a flexible framework for transforming Pandas DataFrames using a modular pipeline approach. Transformations are defined in a YAML configuration, and are applied sequentially to your dataset.

By leveraging DataMorph, your pipelines become cleaner, more scalable and easier to debug.

## Features

- Modular and extensible transformation framework.
- Easily configurable via YAML files.
- Supports multiple transformations, including:
  - **AddColumn**: Adds a new column with a constant value.
  - **ColumnsOperator**: Performs a math operation on two columns and stores the result in a new column.
  - **NormalizeColumn**: Applies Z-score normalization.
  - **RemoveColumns**: Drops specified columns.
  - **FillNA**: Replaces missing values with a default.
  - **MergeDataFrames**: Merges two DataFrames based on common keys.
  - And more!
- Supports custom transformations, defined by the user.

## Installation

To install DataMorph in your project:

```sh
pip install git+https://github.com/davideganna/DataMorph.git
```

If you're developing locally:

```sh
git clone https://github.com/davideganna/DataMorph.git
cd datamorphers
pip install -e .
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

print(df)
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
  - AddColumn:
      column_name: food_marker
      value: food

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
        - food_marker
```

### 3. Apply the transformations as defined in the config

Running the pipeline is very simple:

```python
from datamorphers.pipeline import get_pipeline_config, run_pipeline

# Load YAML config
config = get_pipeline_config("config.yaml", pipeline_name='pipeline_food'))

# Run pipeline
transformed_df = run_pipeline(df, config)

print(transformed_df)
```
| item   | item_type   |   price |   discount_pct |   discounted_price |
|:-------|:------------|--------:|---------------:|-------------------:|
| apple  | food        |     3   |           0.1  |               2.7  |
| banana | food        |     2.5 |           0    |               2.5  |
| pasta  | food        |     3   |           0.12 |               2.64 |
| cake   | food        |    15   |           0    |              15    |

---

## Extending `datamorphers` with Custom Implementations

The `datamorphers` package allows you to define custom transformations by implementing your own DataMorphers. These custom implementations extend the base ones and can be used seamlessly within the pipeline.

### Creating a Custom DataMorpher

To define a custom transformation, create a `custom_datamorphers.py` file in your project and implement a new class that follows the `DataMorpher` structure:

```python
import pandas as pd
from datamorphers.datamorphers import DataMorpher

class CustomTransformer(DataMorpher):
    def __init__(self, column_name: str, value: float):
        self.column_name = column_name
        self.value = value

    def _datamorph(self, df: pd.DataFrame) -> pd.DataFrame:

        Implement your custom transformations here!

        return df
```

---

### Importing Custom DataMorphers

To use your custom implementations, ensure you import both the base `datamorphers` and your custom module:

```python
from datamorphers import datamorphers
import custom_datamorphers
```

The pipeline will first check for the specified DataMorpher in `custom_datamorphers`. If it's not found, it will fall back to the default ones in `datamorphers`. This allows for seamless extension without modifying the base package.

---

### Running the Pipeline with Custom DataMorphers

When defining a pipeline configuration (e.g., in a YAML file), simply reference your custom DataMorpher as you would with a base one:

```yaml
custom_pipeline:
  CustomTransformer:
    column_name: price
    value: 1.2
```

Then, execute the pipeline as usual:

```python
df_transformed = run_pipeline(df, config)
```

If a custom module is provided, your custom transformations will be used instead of or in addition to the built-in ones.

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
