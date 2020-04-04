"""
# ============================================================================
# MOVING_AVERAGE.PY
# ----------------------------------------------------------------------------
# Contains functions for moving averages to be applied to stock data.
#
# ============================================================================
"""

# Imports.
from ..utils.utils import check_and_convert_value_to_list


def simple_moving_average(df_input, from_cols, windows):
    """
    Calculates the simple moving average using a specific column.
    Columns are named SMA_X, where X is the number of days
    of the window size, or SMA_X(col_name) if more than
    one column is used.
    
    Args:
        df_input (pandas.DataFrame): Table with stock data.
        
        from_cols (str, list): The column name or list of names for
         which to calculate the average.
        
        windows (int, list): The window or list of windows, in days, for which
         to calculate the moving average.
    
    Returns:
        (pandas.DataFrame): The stock data table with the moving
         average columns added.
    """
    # Copy input column.
    df = df_input.copy()
    
    # Handle list variables.
    from_cols = check_and_convert_value_to_list(from_cols, str)
    windows = check_and_convert_value_to_list(windows, int)
    
    # Loops through columns and windows, adding new columns.
    for col in from_cols:
        for w in windows:
            col_name = f"SMA_{str(w)}"
            if len(from_cols) > 1:
                col_name += f"({col})"
            df[col_name] = df[col].rolling(window=w).mean()
    
    return df


def exp_moving_average(df_input, from_cols, windows):
    """
    Calculates the exponential moving average using a specific column.
    Columns are named SMA_X, where X is the number of days
    of the window size, or SMA_X(col_name) if more than
    one column is used.
    
    Args:
        df_input (pandas.DataFrame): Table with stock data.
        
        from_cols (str, list): The column name or list of names for
         which to calculate the average.
        
        windows (int, list): The window or list of windows, in days, for which
         to calculate the moving average.
    
    Returns:
        (pandas.DataFrame): The stock data table with the moving
         average columns added.
    """
    # Copy input column.
    df = df_input.copy()
    
    # Handle list variables.
    from_cols = check_and_convert_value_to_list(from_cols, str)
    windows = check_and_convert_value_to_list(windows, int)
    
    # Loops through columns and windows, adding new columns.
    for col in from_cols:
        for w in windows:
            col_name = f"EMA_{str(w)}"
            if len(from_cols) > 1:
                col_name += f"({col})"
            df[col_name] = df[col].ewm(span=w).mean()
    
    return df
