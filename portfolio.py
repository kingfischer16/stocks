"""
# ============================================================================
# PORTFOLIO.PY
# ----------------------------------------------------------------------------
# Contains the 'Portfolio' class and associated methods for tracking and
# monitoring a portfolio. Makes use of the 'StockData' class.
#
# ============================================================================
"""

# Imports.
import pandas as pd
from .stock_data import StockData
from IPython.display import display


class Portfolio:
    """
    Container class for containing and tracking a portfolio.
    
    Args:
        d_portfolio (dict): A dictionary describing the portfolio following
         the format of a dictionary of lists of tuples, where the tuples are
         transaction data, transaction quantity (positive for buy, negative
         for sell), and transaction price::
             d_portfolio = {
                'SYM1': [
                    ('2020-01-30', 20, 1.02),
                    ('2020-02-15', -10, 2.10),
                    ('2020-03-10', 100, 1.50)
                ],
                'SYM2': [
                    ('2020-01-04', 50, 15.30),
                    ('2020-02-02', 25, 30.60)
                ]
            }
    """
    def __init__(self, d_portfolio, stock_data_folder):
        """
        Constructor.
        """
        # Build labels list and trade DataFrame.
        self.labels = list(d_portfolio.keys())
        ls_trades = []
        for sym, data in d_portfolio.items():
            add_list = [{
                'Stock': sym,
                'transact_date': tup[0],
                'transact_quantity': tup[1],
                'transact_price': tup[2]
                } for tup in data]
            ls_trades += add_list
        
        self.df_trades = pd.DataFrame(ls_trades)
        self.df_trades['transact_date'] = self.df_trades['transact_date'].apply(lambda x: pd.to_datetime(x, format='%Y-%m-%d'))
        self.df_trades = self.df_trades.sort_values('transact_date')
        
        # Create StockData object.
        self.sd = StockData(stock_data_folder)
        self.sd.add_and_update(self.labels)
        self.sd.load()
        
        for sym in self.df_trades.Stock.unique():
            current_price = self.sd.get_stock_price(sym)
            self.df_trades.loc[self.df_trades.Stock==sym, 'Holding'] = self.df_trades.loc[self.df_trades.Stock==sym, 'transact_quantity'].cumsum()
            self.df_trades.loc[self.df_trades.Stock==sym, 'Realized'] = self.df_trades.loc[self.df_trades.Stock==sym]\
                                .apply(lambda r: max(0, -r['transact_quantity']*r['transact_price']),
                                       axis=1)
            self.df_trades.loc[self.df_trades.Stock==sym, 'Unrealized'] = self.df_trades.loc[self.df_trades.Stock==sym]\
                                                    .apply(lambda r: max(0, r['Holding']*current_price),
                                                           axis=1)
        self.df_trades['Action'] = self.df_trades['transact_quantity'].apply(lambda x: 'Buy' if x>0 else 'Sell')
        self.df_trades = self.df_trades[['Stock', 'Action', 'transact_date', 'transact_price',
                                         'transact_quantity', 'Holding', 'Realized', 'Unrealized']]
        
        
        summary_list = []
        for sym in self.df_trades.Stock.unique():
            summary_list.append(self._summarize_stock(self.df_trades[self.df_trades['Stock']==sym], sym))
        
        self.summary_table = pd.DataFrame(summary_list)
    
    
    def trade_tables(self):
        """
        Print out the differnt stock tables and trades.
        """
        for sym in self.df_trades['Stock'].unique():
            print(f"\n   ===   {sym}   ===   ")
            display(self.df_trades[self.df_trades['Stock']==sym])
        
    
    
    def _summarize_stock(self, df, label):
        """
        Summarizes the stock data to a single row.
        """
        dfi = df.copy()
        total_bought =  dfi.loc[dfi.transact_quantity>0, 'transact_quantity'].sum()
        total_paid = dfi.loc[dfi.transact_quantity>0]\
                        .apply(lambda r: r['transact_quantity']*r['transact_price'], axis=1).sum()
        average_paid = total_paid / total_bought
        total_sold = dfi.loc[dfi.transact_quantity<0, 'transact_quantity'].sum()
        if not dfi.loc[dfi.transact_quantity<0].empty:
            total_realized = dfi.loc[dfi.transact_quantity<0]\
                                .apply(lambda r: r['transact_quantity']*r['transact_price'], axis=1).sum()
        else:
            total_realized = 0
        remaining_holding = total_bought+total_sold
        remaining_invested = remaining_holding * average_paid
        current_price = self.sd.get_stock_price(label)
        remaining_unrealized = remaining_holding * current_price
        gol = remaining_unrealized - remaining_invested
        frac_return = gol / remaining_invested
        
        return {'Stock': label,
                'Avg. Bought Price': round(average_paid, 2),
                'Current Price': round(current_price, 2),
                'Total Bought': total_bought,
                'Total Sold': total_sold,
                'Current Holding': remaining_holding,
                'Total Invested': round(total_paid, 2),
                'Current Invested': round(remaining_invested, 2),
                'Realized Amount': round(-total_realized, 2),
                'Unrealized Amount': round(remaining_unrealized, 2),
                'Unrealized Gain': round(gol, 2),
                '% Unrealized Gain': f"{round(frac_return*100, 2)} %"}
    
    
    def plot_portfolio(self):
        """
        Plots the stocks in the portfolio.
        """
        self.sd.plot_compare_multiple(self.labels,
                                      period='max',
                                      width=900, height=400)
    
    
    def plot_portfolio_detailed(self):
        """
        Creates a series of detailed single plots for each stock in the portfolio.
        """
        for sym in self.labels:
            print(f"   ===   {sym}   ===   ")
            self.sd.plot_single_analysis(sym)
