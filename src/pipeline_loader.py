import yaml
import logging
import src.datamorphers as datamorphers

logger = logging.Logger(__name__)

def get_pipeline_config(yaml_path):
    with open(yaml_path, 'r') as yaml_config:
        config = yaml.safe_load(yaml_config)
    return config

def run_pipeline(df, config):
    for cls, args in config['pipeline'].items():
        try:
            datamorpher = getattr(datamorphers, cls)(**args)
            df = datamorpher._datamorph(df)
        except Exception as exc:
            logger.error(exc)
    return df 
        
