"""
# ============================================================================
# UTILS.PY
# ----------------------------------------------------------------------------
# Utility functions.
#
# ============================================================================
"""

# Imports.
import warnings
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
    df['FracDividends'] = df['Dividends'] / df['Close']
    df = add_year_month_quarter(df, date_col='Date')
    # Make Dividends column equal to Nan when zero.
    
    return df


def arrange_data_for_chart(d_data, labels=None, column='Close'):
    """
    Creates a single DataFrame from the source dictionary, and
    arrange it for easy use in Altair.
    
    Args:
        d_data (dict): A dictionary of pandas.DataFrames.
        
        labels (str, list): A single string or list of strings
         of the symbols indicating the stock or stocks to be
         updated. Default is None, which updates all stocks
         found in the data directory.
    """
    # Handle labels list if string or None.
    if isinstance(labels, type(None)):
        labels = [l.lower() for l in d_data.keys()]
    else:
        labels = check_and_convert_value_to_list(labels, str)
    
    # Warning for large number of data points.
    if len(labels) > 25:
        warnings.warn("More than 25 separate series are present, which will be difficult to visualize. Consider plotting fewer series at once.")
    
    # Get relevant data for each label.
    df_list = []
    for label in labels:
        df_temp = d_data[label][['Date', column]].copy()
        df_temp = df_temp.loc[df_temp[column]>0]
        df_temp['Symbol'] = label.upper()
        df_list.append(df_temp)
    
    # Concatenate all data.
    df = pd.concat(df_list)
    
    return df
