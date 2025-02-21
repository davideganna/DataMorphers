import yaml
import logging
import src.transformers as transformers

logger = logging.Logger(__name__)

def get_pipeline_config(yaml_path):
    with open(yaml_path, 'r') as yaml_config:
        config = yaml.safe_load(yaml_config)
    return config

def run_pipeline(df, config):
    for func, args in config['pipeline'].items():
        try:
            df = getattr(transformers, func)(df, **args)
        except Exception as exc:
            logger.error(exc)
    return df 
        
