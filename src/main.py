import pandas as pd
from pipeline_loader import get_pipeline_config, run_pipeline

df = pd.DataFrame(
    {
        'A': [1, 2, 3],
        'B': [4, 5, 6]
    }
)

config = get_pipeline_config()
df = run_pipeline(df, config=config)

print(df)