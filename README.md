# DataMorphers

## Overview

DataMorphers is a Python library that provides a framework for transforming Pandas DataFrames using a modular and configurable approach. Each transformation is implemented as a **DataMorpher**, allowing users to sequentially apply transformations using a YAML configuration.

## Features

- Modular and extensible transformation framework.
- Easily configurable via YAML files.
- Supports multiple transformations, including:
  - **CreateColumn**: Add a new column with a constant value.
  - **MultiplyColumns**: Multiply two columns and store the result in a new column.
  - **NormalizeColumn**: Apply Z-score normalization.
  - **RemoveColumn**: Drop specified columns.
  - **FillValue**: Replace missing values with a default.
  - **MergeDataFrames**: Merge two DataFrames based on common keys.
  - And more!

## Installation

To install DataMorphers in your project:

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

### 1. Define Your Transformation Pipeline

Create a YAML file specifying the transformations:

```yaml
pipeline:
  CreateColumn:
    column_name: "new_col"
    value: 42

  MultiplyColumns:
    first_column: "col1"
    second_column: "col2"
    output_column: "product_col"

  MergeDataFrames:
    df_to_join: "df_extra"
    join_cols: ["id"]
    how: "left"
```

### 2. Apply Transformations in Python

```python
import pandas as pd
from datamorphers.pipeline import run_pipeline

# Sample DataFrame
df = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})
extra_df = pd.DataFrame({"id": [1, 2, 3], "value": [10, 20, 30]})

# Load YAML config
config = get_pipeline_config("config.yaml")

# Run pipeline
transformed_df = run_pipeline(df, config, extra_dfs={"df_extra": extra_df})
print(transformed_df)
```

## Extending DataMorphers

You can create custom transformations by extending the `DataMorpher` class inside a module named `custom_datamorphers.py`:

```python
from datamorphers.datamorphers import DataMorpher

class CustomTransform(DataMorpher):
    def _datamorph(self, df: pd.DataFrame) -> pd.DataFrame:
        df["custom_col"] = df["existing_col"] * 2
        return df
```

## Running Tests

DataMorphers uses **pytest** for testing. To run tests:

```sh
pytest -v
```

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
