"""
# ============================================================================
# RETURNS.PY
# ----------------------------------------------------------------------------
# Contains the 'StockData' class and associated methods for importing
# stock data using the 'yfinance' package, as well as calculating
# metrics and averaging data.
#
# ============================================================================
"""

# Imports.
from datetime import date
import pandas as pd
from ..utils.utils import check_and_convert_value_to_list


def calculate_daily_returns(df_input, price_col='Close'):
    """
    Calculates the daily returns off a specified column.
    
    Args:
        df_input (pandas.DataFrame): Input data.
        
        price_col (str): The name of the column containing the price data.
    
    Returns:
        (pandas.DataFrame): The input data with a 'DailyReturn' column added.
    """
    df = df_input.copy()
    df['DailyReturns'] = df[price_col].diff(1) / df[price_col].shift(1)
    return df


def calculate_grouped_returns(df_input, new_col_name, price_col='Close', group_cols=[]):
    """
    Calculates and joins the returns column based on grouping columns.
    
    Args:
        df_input (pandas.DataFrame): The input data.
        
        new_col_name (str): The name of the new returns column.
        
        price_col (str): The name of the column containing the price data.
        
        group_cols (str, list): Column name or names to group by for the returns.
    
    Returns:
        (pandas.DataFrame): The table with the new returns column joined.
    """
    df = df_input.copy()
    group_cols = check_and_convert_value_to_list(group_cols, str)
    df_grouped = df.groupby(group_cols).agg({price_col: ['first', 'last'],
                                             'Date': 'last'})
    df_grouped.columns=['price_first', 'price_last', 'date_last']
    df_grouped = df_grouped.reset_index(drop=True)
    df_grouped[new_col_name] = (df_grouped['price_last'] - 
                                df_grouped['price_first'])/df_grouped['price_first']
    df = df.rename(columns={'Date': 'DateCol'})
    df = df.merge(df_grouped[[new_col_name, 'date_last']], how='left',
                  left_on='DateCol', right_on='date_last')
    df = df.rename(columns={'DateCol': 'Date'})
    return df.drop('date_last', axis=1)

    
def calculate_monthly_returns(df_input, price_col='Close'):
    """
    Calculates the returns per month.
    """
    return calculate_grouped_returns(df_input,
                                     'MonthlyReturns',
                                     price_col,
                                     ['year', 'month'])


def calculate_quarterly_returns(df_input, price_col='Close'):
    """
    Calculates the returns per quarter.
    """
    return calculate_grouped_returns(df_input,
                                     'QuarterlyReturns',
                                     price_col,
                                     ['Q'])


def calculate_annual_returns(df_input, price_col='Close'):
    """
    Calculates the returns per year.
    """
    return calculate_grouped_returns(df_input,
                                     'AnnualReturns',
                                     price_col,
                                     ['year'])


def average_returns_summary(df_input, base_col='DailyReturns', avg_period='Monthly'):
    """
    Average specific returns over a given period.
    """
    df = df_input[['Date', base_col, 'Q', 'year', 'month']].copy()
    if avg_period.lower() == 'monthly':
        df = calculate_monthly_returns(df, price_col=base_col)
        df = df.rename(columns={'MonthlyReturns': f"{base_col}-averaged-Monthly"})
    elif avg_period.lower() == 'quarterly':
        df = calculate_quarterly_returns(df, price_col=base_col)
        df = df.rename(columns={'QuarterlyReturns': f"{base_col}-averaged-Quarterly"})
    elif avg_period.lower() == 'annually':
        df = calculate_annual_returns(df, price_col=base_col)
        df = df.rename(columns={'AnnualReturns': f"{base_col}-averaged-Annually"})
    else:
        raise ValueError(f"Argument 'avg_period' must be one of: 'monthly', 'quarterly', 'annually'")
    return df


def dividend_summary(df_input, symbol, div_type='FracDividends'):
    """
    Summarizes the history of fractional dividends (dividends per dollar equity).
    """
    _year_ = date.today().year
    last_year = _year_ - 1
    five_years_ago = last_year - 5
    df = df_input.loc[(df_input[div_type].notnull())&(df_input[div_type]>0)].copy()
    d_div = {'Symbol': symbol.upper(),
             f'Overall Average {div_type}': df[div_type].mean(),
             f'Last 5 Years Average': df.loc[df['year']>=five_years_ago, div_type].mean(),
             f'{last_year} Average': df.loc[df['year']>=last_year, div_type].mean()}
    return d_div