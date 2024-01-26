import pandas as pd


class InvalidSymbol(Exception):
    pass


def ohlc_df_normalize(df: pd.DataFrame) -> pd.DataFrame:
    """
    normalizes ohlc df
    """
    rename_mapping = {}
    for column in df.columns.tolist():
        rename_mapping[column] = column.title()
    df = df.rename(columns=rename_mapping)
    return df
