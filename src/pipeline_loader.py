import yaml
import logging
import transformers

logger = logging.Logger(__name__)

def get_pipeline_config():
    with open('test_pipeline.yaml', 'r') as file:
        config = yaml.safe_load(file)
    return config

def run_pipeline(df, config):
    for k, v in config['pipeline'].items():
        try:
            df = getattr(transformers, k)(df, **v)
        except Exception as exc:
            logger.error(exc)
    return df 
        
