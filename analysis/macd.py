"""
# ============================================================================
# MACD.PY
# ----------------------------------------------------------------------------
# Functions used to calculate the Moving Average Convergence Divergence.
# 
# References:
#     [1] https://www.investopedia.com/terms/m/macd.asp
#
# ============================================================================
"""

# Imports.
from .moving_average import exp_moving_average


def macd(df_input, price_column):
    """
    Moving Average Convergence Divergence (MACD) is defined as the
    12-period EMA minus the 26-period EMA. This function adds 3 columns
    to the pandas.DataFrame, the two EMAs plus the MACD.
    
    Args:
        df_input (pandas.DataFrame): The stock data table.
        
        price_column (str): The price column to use for the calculation.
         Typically is the 'Close' column.
    
    Returns:
        (pandas.DataFrame): The stock data table with the new columns.
    """
    # Copy the DataFrame.
    df = df_input.copy()
    
    # Calcuate the moving averages.
    df = exp_moving_average(df, price_column, [12, 26])
    
    # Calculate the MACD.
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    
    return df
