import pandas as pd
from src.pipeline_loader import get_pipeline_config, run_pipeline

def generate_mock_df():
    df = pd.DataFrame(
        {
            'A': [1, 2, 3],
            'B': [4, 5, 6]
        }
    )
    return df

def test_full_pipeline():
    df = generate_mock_df()
    config = get_pipeline_config(yaml_path='tests/test_pipeline.yaml')
    df = run_pipeline(df, config=config)
    
    print('\n')
    print(df)