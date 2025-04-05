# ⚙️ DataMorphers

![Unit Tests](https://github.com/davideganna/DataMorph/actions/workflows/tests.yaml/badge.svg)
[![codecov](https://codecov.io/gh/davideganna/DataMorphers/graph/badge.svg?token=MXTUZEDC44)](https://codecov.io/gh/davideganna/DataMorphers)
![Ruff Lint](https://img.shields.io/badge/code%20style-ruff-blue)
![PyPI version](https://img.shields.io/pypi/v/datamorphers.svg)

<p align="center">
  <img src="https://github.com/user-attachments/assets/f1b01b79-4032-4688-82a1-c586a7ee9f9a" width=420>
</p>

## Overview

DataMorphers provides a flexible framework for transforming Pandas and Polars DataFrames using a modular data pipeline approach. Transformations are defined in a YAML configuration, and are applied sequentially to your dataset.

By leveraging DataMorphers, your pipelines become cleaner, more scalable and easier to debug.

## Features

- Modular and extensible transformation framework to design data pipelines, easily configurable from YAML files.
- Supports multiple transformations, alphabetically ordered here (more to come!):

  - [CreateColumn](https://github.com/davideganna/DataMorphers/search?q=class+CreateColumn&type=code)
  - [CastColumnTypes](https://github.com/davideganna/DataMorphers/search?q=class+CastColumnTypes&type=code)
  - [ColumnsOperator](https://github.com/davideganna/DataMorphers/search?q=class+ColumnsOperator&type=code)
  - [DropDuplicates](https://github.com/davideganna/DataMorphers/search?q=class+DropDuplicates&type=code)
  - [DropNA](https://github.com/davideganna/DataMorphers/search?q=class+DropNA&type=code)
  - [FillNA](https://github.com/davideganna/DataMorphers/search?q=class+FillNA&type=code)
  - [FilterRows](https://github.com/davideganna/DataMorphers/search?q=class+FilterRows&type=code)
  - [FlatMultiIndex](https://github.com/davideganna/DataMorphers/search?q=class+FlatMultiIndex&type=code)
  - [MergeDataFrames](https://github.com/davideganna/DataMorphers/search?q=class+MergeDataFrames&type=code)
  - [NormalizeColumn](https://github.com/davideganna/DataMorphers/search?q=class+NormalizeColumn&type=code)
  - [RemoveColumns](https://github.com/davideganna/DataMorphers/search?q=class+RemoveColumns&type=code)
  - [RenameColumns](https://github.com/davideganna/DataMorphers/search?q=class+RenameColumns&type=code)
  - [Rolling](https://github.com/davideganna/DataMorphers/search?q=class+Rolling&type=code)
  - [SelectColumns](https://github.com/davideganna/DataMorphers/search?q=class+SelectColumns&type=code)
  - [ToLower](https://github.com/davideganna/DataMorphers/search?q=class+ToLower&type=code)
  - [ToUpper](https://github.com/davideganna/DataMorphers/search?q=class+ToUpper&type=code)

- Supports custom transformations, defined by the user.
- Supports storing and retrieving objects throughout the entire application lifecycle, by leveraging [DataMorphersStorage](https://github.com/davideganna/DataMorphers/search?q=class+DataMorphersStorage&type=code)

## Installation

Install DataMorphers in your project directly from PyPI:

```sh
pip install datamorphers
```

## Usage

### 1. Define your initial DataFrame

| item   | item_type   | price | discount_pct |
| :----- | :---------- | ----: | -----------: |
| apple  | food        |     3 |          0.1 |
| TV     | electronics |   100 |         0.05 |
| banana | food        |   2.5 |          nan |
| pasta  | food        |     3 |         0.12 |
| cake   | food        |    15 |          nan |

### 2. Define Your Transformation Pipeline

Imagine that we want to perform some actions on the original DataFrame.
Specifically, we want to identify which items are food, and then calculate the price after a discount percentage is applied. After these operations, we want to polish the DataFrame by removing non interesting columns.

To do so, we create a YAML file specifying a pipeline of transformations, named `config.yaml`:

```yaml
pipeline_food:
  # Compare the column "item_type" with the value "food", and keep rows that are equal (logic: "eq").
  - FilterRows:
      first_column: item_type
      second_column: food
      logic: eq

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
- INFO -     columns_name: ['discount_amount']
```

The resulting DataFrame follows:
| item | item_type | price | discount_pct | discounted_price |
|:-------|:------------|--------:|---------------:|-------------------:|
| apple | food | 3 | 0.1 | 2.7 |
| banana | food | 2.5 | 0 | 2.5 |
| pasta | food | 3 | 0.12 | 2.64 |
| cake | food | 15 | 0 | 15 |

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

## Storing and retrieving objects through `DataMorphersStorage`

DataMorphers provides a Singleton-Based storage system, called `DataMorphersStorage`.

This is a singleton-based, in-memory key-value storage designed for shared access across multiple modules in a Python application. It ensures that only one instance of the storage exists, maintaining a persistent cache across imports.

Features:

- In-Memory Storage – Stores data without relying on external databases.

- Logging Support – Integrates with the `datamorphers.logger` module for logging.

- Cache Persistence – Retains stored data across module imports.

- Utility Methods – Includes `set()`, `get()`, `isin()`, `list_keys()`, and `clear()`.

### Usage

Import the `DataMorphersStorage` instance

```python
from datamorphers.storage import dms
```

Store an object:

```python
dms.set("df_transformed", df_transformed)
```

Retrieve an object:

```python
df_transformed = dms.get("df")
```

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
