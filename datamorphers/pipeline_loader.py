import yaml
import logging
import datamorphers.datamorphers as datamorphers
import importlib
import pandas as pd
from typing import Any
from datamorphers.base import DataMorpher

logger = logging.getLogger(__name__)


def get_pipeline_config(yaml_path: str, pipeline_name: str) -> dict:
    with open(yaml_path, "r") as yaml_config:
        config = yaml.safe_load(yaml_config)
    config["pipeline_name"] = pipeline_name
    return config


def log_pipeline_config(config: dict):
    logger.info("Loading the following pipeline:")
    _dm: dict
    for _dm in config[f"{config['pipeline_name']}"]:
        for cls, args in _dm.items():
            logger.info(f"*** DataMorpher ***: {cls} ")
            for arg, value in args.items():
                logger.info(f"  {arg}: {value}")


def run_pipeline(df: pd.DataFrame, config: Any, extra_dfs: dict = {}):
    """
    Runs the pipeline transformations sequentially.

    :param df: The main DataFrame to be transformed.
    :param config: The pipeline configuration dictionary.
    :param extra_dfs: A dictionary containing additional DataFrames
        required by certain DataMorphers.

    :returns: Transformed DataFrame.
    """

    # Try to install custom_datamorphers, a module where the user can define
    #   their specific transformations.
    try:
        custom_datamorphers = importlib.import_module("custom_datamorphers")
        logger.info("Successfully imported module custom_datamorphers.")
    except ModuleNotFoundError:
        logger.info(
            "Module custom_datamorphers not found. Custom DataMorphers implementations will not be loaded.\n"
        )
        custom_datamorphers = None

    # Display pipeline configuration
    log_pipeline_config(config)

    # Define the single DataMorpher inside a list of DataMorphers
    _dm: dict

    for _dm in config[f"{config['pipeline_name']}"]:
        for cls, args in _dm.items():
            try:
                # Try getting the class from custom datamorphers first so that
                #   custom DataMorphers override default ones.
                if custom_datamorphers and hasattr(custom_datamorphers, cls):
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
