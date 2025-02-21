import pandas as pd

def add_column(df, col, val):
    df[col] = val
    return df