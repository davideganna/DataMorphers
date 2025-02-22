import yaml
import logging
import datamorphers.datamorphers as datamorphers
import datamorphers.custom_datamorphers as custom_datamorphers
import pandas as pd
from typing import Any
from datamorphers.base import DataMorpher

logger = logging.Logger(__name__)


def get_pipeline_config(yaml_path: str, pipeline_name: str):
    with open(yaml_path, 'r') as yaml_config:
        config = yaml.safe_load(yaml_config)
    config['pipeline_name'] = pipeline_name
    return config


def run_pipeline(df: pd.DataFrame, config: Any, extra_dfs: dict={}):
    """
    Runs the pipeline transformations sequentially.

    :param df: The main DataFrame to be transformed.
    :param config: The pipeline configuration dictionary.
    :param extra_dfs: A dictionary containing additional DataFrames
        required by certain DataMorphers.

    :returns: Transformed DataFrame.
    """
    for cls, args in config[f"{config['pipeline_name']}"].items():
        try:
            # Try getting the class from custom datamorphers first so that
            #   custom DataMorphers override default ones.
            if hasattr(custom_datamorphers, cls):
                module = custom_datamorphers
            elif hasattr(datamorphers, cls):
                module = datamorphers
            else:
                raise ValueError(f"Unknown DataMorpher: {cls}")

            # Get the DataMorpher class
            datamorpher_cls: DataMorpher = getattr(module, cls)

            # Should the class require extra DataFrames (e.g., MergeDataFrames DataMorpher),
            #   the args are handled here.
            args = datamorpher_cls._handle_args(args, extra_dfs)

            # Instantiate the DataMorpher object with the updated args.
            datamorpher: DataMorpher = datamorpher_cls(**args)

            # Transform the DataFrame.
            df = datamorpher._datamorph(df)

        except Exception as exc:
            logger.error(f"Error in {cls}: {exc}")

    return df
