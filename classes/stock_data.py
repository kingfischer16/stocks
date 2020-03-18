"""
# ============================================================================
# STOCK_DATA.PY
# ----------------------------------------------------------------------------
# Contains the 'StockData' class and associated methods for importing
# stock data using the 'yfinance' package, as well as calculating
# metrics and averaging data.
#
# ============================================================================
"""

# Imports.
import os
import pandas as pd
import yfinance as yf


class StockData:
    """
    Containing class for saving and updating stock data.
    
    Args:
        data_folder (str): Path to saved data, and where
         data will be saved.
    """
    def __init__(self, data_folder):
        """
        Constructor.
        """
        # Get list of folders.
        dir_list = next(os.walk(data_folder))[1]
        if not dir_list:
            print(f"Folder '{data_folder}' has no data.")
        else:
            print(f"Folder 'data_folder' the following stocks:\n\t|")
            for folder in dir_list:
                print(f"\t|-- {folder.upper()}")
