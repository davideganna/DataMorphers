import yaml
import importlib
import pandas as pd
import datamorphers.datamorphers as datamorphers
from datamorphers.base import DataMorpher
from datamorphers import logger
from typing import Any


def get_pipeline_config(yaml_path: str, pipeline_name: str) -> dict:
    """
    Loads the pipeline configuration from a YAML file.

    Args:
        yaml_path (str): The path to the YAML configuration file.
        pipeline_name (str): The name of the pipeline to load.

    Returns:
        dict: The pipeline configuration dictionary.
    """
    with open(yaml_path, "r") as yaml_config:
        config = yaml.safe_load(yaml_config)
    config["pipeline_name"] = pipeline_name
    return config


def log_pipeline_config(config: dict):
    """
    Logs the pipeline configuration.

    Args:
        config (dict): The pipeline configuration dictionary.
    """
    logger.info(f"Loading pipeline named: {config['pipeline_name']}")
    _dm: dict | str
    for _dm in config[f"{config['pipeline_name']}"]:
        if isinstance(_dm, dict):
            cls, args = list(_dm.items())[0]

        elif isinstance(_dm, str):
            cls, args = _dm, {}

        else:
            raise ValueError(f"Invalid DataMorpher format: {_dm}")

        logger.info(f"*** DataMorpher: {cls} ***")
        for arg, value in args.items():
            logger.info(f"{4*' '}{arg}: {value}")


def run_pipeline(df: pd.DataFrame, config: Any, extra_dfs: dict = {}):
    """
    Runs the pipeline on the DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame to be transformed.
        config (Any): The pipeline configuration.
        extra_dfs (dict, optional): Additional DataFrames required by some DataMorphers. Defaults to {}.

    Returns:
        pd.DataFrame: The transformed DataFrame.
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
    _dm: dict | str

    for _dm in config[f"{config['pipeline_name']}"]:
        if isinstance(_dm, dict):
            cls, args = list(_dm.items())[0]

        elif isinstance(_dm, str):
            cls, args = _dm, {}

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
