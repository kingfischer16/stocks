"""
# ============================================================================
# PLOTTING.PY
# ----------------------------------------------------------------------------
# As the extremely original name suggests, this contains some plotting
# functions for stock data. Plots are created with the 'altair' package
# and are interactive.
#
# ============================================================================
"""

# Imports.
import pandas as pd
import altair as alt
from ..utils.utils import arrange_data_for_chart


def line_chart(d_data, x_col='Date', y_col='Close', labels=None,
               label_col='Symbol', width=800, height=400):
    """
    Creates a line plot using altair.
    
    Args:
        data (pandas.DataFrame): Source data for stock.
        
        x_col (str): Column name for x-axis data.
        
        y_col (str): Column name for y-axis data.
        
        width (int): Chart width in pixels.
        
        height (int): Chart height in pixels.
    
    Returns:
        (altair.vegalite.v4.api.Chart): Altair chart object.
    """
    source = arrange_data_for_chart(d_data, labels, y_col)
    line = alt.Chart(source)\
            .properties(width=width, height=height)\
            .mark_line()\
            .encode(
                x=f'{x_col}:T',
                y=y_col,
                color=label_col)\
            .interactive(bind_y=False)
    return line


def candlestick_chart(source, width=900, height=400):
    """
    Produces a candlestick chart from open, close, high,
    and low data.
    
    Args:
        source (pandas.DataFrame): Stock data with EMA columns.
        
        width (int): Chart width in pixels.
        
        height (int): Total chart height in pixels.
    
    Returns:
        (altair.vegalite.v4.api.Chart): Altair chart object.
    """
    open_close_color = alt.condition("datum.Open < datum.Close",
                                 alt.value("#06982d"),
                                 alt.value("#ae1325"))

    rule = alt.Chart(source).mark_rule().encode(
        alt.X(f'Date:T'),
        alt.Y('Low', title='Price', scale=alt.Scale(zero=False),
        ),
        alt.Y2('High'),
        color=alt.value('#000000')
    ).properties(width=width, height=height).interactive(bind_y=False)

    bar = alt.Chart(source).mark_bar().encode(
        x='Date:T',
        y='Open',
        y2='Close',
        color=open_close_color
    )

    return rule + bar


def macd_chart(source, width=900, height=600):
    """
    Calculates the MACD (DIF) and OSC. The below logic
    applies and should be used to signal:
    
    1. When DIF and DEA are positive, the MACD line passes (exceeds) the
     OSC line going upwards, and the divergence is positive,
     there is a buy signal confrmation.
    2. When DIF and DEA are negative, the MACD line exceeds the OSC line
     going downwards, and the divergence is negative, there is a
     sell signal confrmation.
    
    Args:
        source (pandas.DataFrame): Stock data with EMA columns.
        
        width (int): Chart width in pixels.
        
        height (int): Total chart height in pixels.
    
    Returns:
        (altair.vegalite.v4.api.Chart): Altair chart object.
    """
    # Common axis zoom selector for both charts.
    zoom = alt.selection_interval(bind='scales', encodings=['x'])
    
    # Coloration based on closing price being higher or
    # lower than opening price.
    open_close_color = alt.condition("datum.MACD > datum.DEA",
                                 alt.value("#06982d"),
                                 alt.value("#ae1325"))
    
    # Get MACD and signal line in correct form.
    df_list = []
    for d in ['MACD', 'DEA']:
        df_temp = source[['Date', d]].copy()
        df_temp = df_temp.rename(columns={d: 'VALUE'})
        df_temp['Label'] = d
        df_list.append(df_temp)
    df1 = pd.concat(df_list)
    
    macd_lines = alt.Chart(df1)\
                .properties()\
                .mark_line()\
                .encode(
                    x='Date:T',
                    y='VALUE',
                    color='Label',
                    opacity=alt.value(0.8))
    
    # Colored bars for MACD.
    bar = alt.Chart(source).mark_bar()\
            .properties(width=width, height=int(height*0.3))\
            .encode(
                x='Date:T',
                y='OSC',
                color=open_close_color)\
            .add_selection(zoom)
    
    # Candlestick chart.
    candle = candlestick_chart(source, width=width, height=int(0.7*height))
    
    # Add EMA_12 and EMA_26 to the Candlestick chart.
    df_list = []
    for d in ['EMA_12', 'EMA_26']:
        df_temp = source[['Date', d]].copy()
        df_temp = df_temp.rename(columns={d: 'VALUE'})
        df_temp['Label'] = d
        df_list.append(df_temp)
    df2 = pd.concat(df_list)
    
    ema_lines = alt.Chart(df2)\
                .properties()\
                .mark_line()\
                .encode(
                    x='Date:T',
                    y='VALUE',
                    color='Label')\
                .add_selection(zoom)
    
    return alt.vconcat(candle + ema_lines, bar + macd_lines)
