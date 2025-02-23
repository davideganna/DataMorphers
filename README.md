# DataMorphers

## Overview

DataMorph is a Python library that provides a framework for transforming Pandas DataFrames using a modular pipeline approach. Transformations are defined in a YAML configuration, and are applied sequentially to your dataset.

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

# Extending `datamorphers` with Custom Implementations

The `datamorphers` package allows you to define custom transformations by implementing your own DataMorphers. These custom implementations extend the base ones and can be used seamlessly within the pipeline.

## 1. Creating a Custom DataMorpher

To define a custom transformation, create a `custom_datamorphers.py` file in your project and implement a new class that follows the `DataMorpher` structure:

```python
import pandas as pd
from datamorphers.datamorphers import DataMorpher

class MultiplyColumnByValue(DataMorpher):
    def __init__(self, column_name: str, value: float, output_column: str):
        self.column_name = column_name
        self.value = value
        self.output_column = output_column

    def _datamorph(self, df: pd.DataFrame) -> pd.DataFrame:
        df[self.output_column] = df[self.column_name] * self.value
        return df
```

---

## 2. Importing Custom DataMorphers

To use your custom implementations, ensure you import both the base `datamorphers` and your custom module:

```python
from datamorphers import datamorphers
import custom_datamorphers  # Import custom transformations
```

The pipeline will first check for the specified DataMorpher in `custom_datamorphers`. If it's not found, it will fall back to the default ones in `datamorphers`. This allows for seamless extension without modifying the base package.

---

## 3. Running the Pipeline with Custom DataMorphers

When defining a pipeline configuration (e.g., in a YAML file), simply reference your custom DataMorpher as you would with a base one:

```yaml
custom_pipeline:
  MultiplyColumnByValue:
    column_name: "price"
    value: 1.2
    output_column: "adjusted_price"
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
