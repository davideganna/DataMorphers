import yaml
import logging
import pandas as pd
import datamorphers.datamorphers as datamorphers
from datamorphers.base import DataMorpher
from datamorphers import logger, custom_datamorphers
from typing import Any


def get_pipeline_config(yaml_path: str, pipeline_name: str, **kwargs: dict) -> dict:
    """
    Loads the pipeline configuration from a YAML file.

    Args:
        yaml_path (str): The path to the YAML configuration file.
        pipeline_name (str): The name of the pipeline to load.
        kwargs (dict): Additional arguments to be evaluated at runtime.

    Returns:
        dict: The pipeline configuration dictionary.
    """
    with open(yaml_path, "r") as yaml_config:
        yaml_content = yaml_config.read()

    # Add runtime evaluation of variables
    for k, v in kwargs.items():
        if isinstance(v, pd.DataFrame):
            # Serialize the DataFrame, which will be deserialized in the specific DataMorpher.
            v = v.to_json()
        yaml_content = yaml_content.replace(f"${{{k}}}", str(v))

    config = yaml.safe_load(yaml_content)
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


def run_pipeline(df: pd.DataFrame, config: Any, debug: bool = False):
    """
    Runs the pipeline on the DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame to be transformed.
        config (Any): The pipeline configuration.
        extra_dfs (dict, optional): Additional DataFrames required by some DataMorphers. Defaults to {}.

    Returns:
        pd.DataFrame: The transformed DataFrame.
    """
    # Get the custom logger
    logger = logging.getLogger("datamorphers")

    # Set logging level based on debug flag
    logger.setLevel(logging.DEBUG if debug else logging.INFO)

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

            # Instantiate the DataMorpher object with the updated args.
            datamorpher: DataMorpher = datamorpher_cls(**args)

            # Transform the DataFrame.
            df = datamorpher._datamorph(df)

            # Log the shape of the DataFrame after each transformation
            logger.debug(f"DataFrame shape after {cls}: {df.shape}")

        except Exception as exc:
            logger.error(f"Error in {cls}: {exc}")

    return df
