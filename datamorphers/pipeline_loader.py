import inspect
import logging
from typing import Any

import pandas as pd
import yaml
from narwhals.typing import IntoFrame

import datamorphers.datamorphers as datamorphers
from datamorphers import custom_datamorphers, logger
from datamorphers.base import DataMorpher


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
            # Serialize the DataFrame, which will be deserialized
            #   in the specific DataMorpher.
            v = v.to_json()
        yaml_content = yaml_content.replace(f"${{{k}}}", str(v))

    config = yaml.safe_load(yaml_content)
    config["pipeline_name"] = pipeline_name

    validate_pipeline_config(config)

    return config


def validate_pipeline_config(config: dict):
    """
    Validates the pipeline configuration before execution.

    Ensures that:
    - The pipeline has a valid name.
    - Each DataMorpher exists.
    - Required arguments are present.
    - No extra arguments are provided.

    Args:
        config (dict): The pipeline configuration dictionary.

    Raises:
        ValueError: If any validation issue is found.
    """
    if "pipeline_name" not in config:
        raise ValueError("Missing 'pipeline_name' in pipeline configuration.")

    for step in config.get(config["pipeline_name"], []):
        if isinstance(step, dict):
            cls, args = list(step.items())[0]
        elif isinstance(step, str):
            cls, args = step, {}
        else:
            raise ValueError(f"Invalid pipeline step format: {step}")

        # Check if the DataMorpher class exists
        module = (
            custom_datamorphers
            if hasattr(custom_datamorphers, cls)
            else datamorphers
            if hasattr(datamorphers, cls)
            else None
        )
        if not module:
            raise ValueError(f"Unknown DataMorpher: {cls}")

        datamorpher_cls = getattr(module, cls)

        # Get all parameters from the __init__ method
        signature = inspect.signature(datamorpher_cls.__init__)
        defined_args = [param for param in signature.parameters if param != "self"]

        # Required arguments (without default values)
        required_args = [
            param
            for param, details in signature.parameters.items()
            if details.default == inspect.Parameter.empty and param != "self"
        ]

        # Check for missing arguments
        missing_args = [arg for arg in required_args if arg not in args]
        if missing_args:
            raise ValueError(f"Missing required arguments for {cls}: {missing_args}")

        # Check for unexpected (extra) arguments
        extra_args = [arg for arg in args if arg not in defined_args]
        if extra_args:
            raise ValueError(f"Unexpected arguments for {cls}: {extra_args}")


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
            logger.info(f"{4 * ' '}{arg}: {value}")


def run_pipeline(df: IntoFrame, config: Any, debug: bool = False) -> IntoFrame:
    """
    Runs the pipeline on the DataFrame.

    Args:
        df (nw.IntoFrame): The input DataFrame to be transformed.
        config (Any): The pipeline configuration.
        debug (bool, default False): Whether to log additional debugging messages.

    Returns:
        nw.IntoFrame: The transformed DataFrame.
    """
    # Get the custom logger
    logger = logging.getLogger("datamorphers")

    # Set logging level based on debug flag
    logger.setLevel(logging.DEBUG if debug else logging.INFO)

    # Display pipeline configuration
    log_pipeline_config(config)

    # Process each step in the pipeline
    for step in config[config["pipeline_name"]]:
        cls, args = list(step.items())[0] if isinstance(step, dict) else (step, {})

        # Get the DataMorpher class
        module = getattr(custom_datamorphers, cls, None) or getattr(datamorphers, cls)
        datamorpher_cls: DataMorpher = module

        # Instantiate the DataMorpher object
        datamorpher: DataMorpher = datamorpher_cls(**args)

        # Transform the DataFrame
        df = datamorpher._datamorph(df)

        # Log the shape of the DataFrame after each transformation
        logger.debug(f"DataFrame shape after {cls}: {df.shape}")

    return df
