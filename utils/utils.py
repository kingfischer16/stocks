"""
# ============================================================================
# UTILS.PY
# ----------------------------------------------------------------------------
# Utility functions.
#
# ============================================================================
"""

# Imports.
import numpy as np
import pandas as pd


def check_and_convert_value_to_list(val_or_list, expected_type):
    """
    Checks to make sure the argument is either of the expected type
    or that the list contains only values of this type. If the argument
    is not a list, it is converted to a list.
    
    Args:
        val_or_list (*, list): A value or a list of values for checking.
        
        expected_type (type): The type to check.
    
    Returns:
        (list): A list of the expected type.
    
    Raises:
        ValueError: if the value or list does not match with the expected type.
    """
    # If it is a list.
    if isinstance(val_or_list, list):
        for val in val_or_list:
            # Handle incorrect type.
            if not isinstance(val, expected_type):
                raise ValueError(f"Value {val} in list is not of expected type {expected_type}.")
        return val_or_list
    # If it is not a list.
    else:
        if not isinstance(val_or_list, expected_type):
            raise ValueError(f"Value {val_or_list} is not of expected type {expected_type}.")
        return [val_or_list]


def add_year_month_quarter(df_init, date_col='Date'):
    """
    Adds the year, month, and quarter numeric columns to the
    stock price data frames.
    
    Args:
        df_init (pandas.DataFrame): The stock price DataFrame.
        
        date_col (str): The name of the date column. Default is 'Date'.
    
    Returns:
        (pandas.DataFrame): The table with new columns.
    """
    # Copy to avoid overwrite.
    df = df_init.copy()
    # Create columns.
    df['year'] = pd.DatetimeIndex(df[date_col]).year
    df['month'] = pd.DatetimeIndex(df[date_col]).month
    df['quarter'] = (df['month']/3).apply(np.ceil).astype(int)
    df['Q'] = df.apply(lambda r: f"{r['year']}-Q{r['quarter']}", axis=1)
    
    return df


def add_columns_on_import(df_input):
    """
    Centralized adding of useful columns.
    
    Args:
        df_input (pandas.DataFrame): The stock price data table.
    
    Returns:
        (pandas.DataFrame): The table with the new columns.
    """
    # Copy to avoid overwrite.
    df = df_input.copy()
    # Add columns.
    df['Date'] = df.index
    df = add_year_month_quarter(df, date_col='Date')
    
    return df
