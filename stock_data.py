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
import warnings
import pickle
import pandas as pd
import yfinance as yf
from .utils.utils import check_and_convert_value_to_list, add_columns_on_import
from .analysis.moving_average import simple_moving_average, exp_moving_average
from .analysis.macd import macd


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
        self.root = data_folder
        self.dir_list = next(os.walk(self.root))[1]
        self.dir_list = [d.lower() for d in self.dir_list]
        if not self.dir_list:
            print(f"Folder '{self.root}' has no data.")
        else:
            print(f"Folder 'data_folder' the following stocks:\n\t|")
            for folder in self.dir_list:
                print(f"\t|-- {folder.upper()}")


    def create_folder_path(self, folder):
        """
        Returns the folder path for the specific stock.
        """
        if self.root[-1] == "/":
            return self.root + folder.lower()
        else:
            return self.root + "/" + folder.lower()


    def add(self, labels):
        """
        Adds the indicated stock or stocks to the StockData object
        and writes the data to the data folder.
        
        Args:
            labels (str, list): A single string or list of strings
             of the symbols indicating the stock or stocks to be
             added.
        """
        labels = check_and_convert_value_to_list(labels, str)
        
        # Loop and add data.
        for label in labels:
            # Warn if the label exists.
            if label in self.dir_list:
                warnings.warn(f"Stock '{label.upper()}' is currently in the data library. Use StockData.update('{label}') to update the stock data.")
                continue
            
            # Construct the local data folder.
            path = self.create_folder_path(label.lower())
            
            # Download data.
            tckr = yf.Ticker(label.upper())
            data = add_columns_on_import(tckr.history(period='max'))
            meta = {
                'symbol': label.upper(),
                'last_date': f"{str(data['Date'].max().year)}-{str(data['Date'].max().month).zfill(2)}-{str(data['Date'].max().day).zfill(2)}"
            }
            
            # Create the folder if it doesn't exist.
            if not os.path.exists(path):
                os.mkdir(path)
            
            # Save data for folder.
            data.to_pickle(f"{path}/data.pkl")
            with open(f"{path}/meta.pkl", "wb") as fp:
                pickle.dump(meta, fp, protocol=pickle.HIGHEST_PROTOCOL)


    def update(labels=None):
        """
        Update to the most recent pricing data and write to file.
        
        Args:
            labels (str, list): A single string or list of strings
             of the symbols indicating the stock or stocks to be
             updated. Default is None, which updates all stocks
             found in the data directory.
        """
        if not self.dir_list:
            return
        
        # Handle labels list if string or None.
        if isinstance(labels, type(None)):
            labels = [l.lower() for l in self.dir_list]
        else:
            labels = check_and_convert_value_to_list(labels, str)
        
        # Loop and udpate data.
        for label in labels:
            # Warn if the label does not currently exist.
            if label not in self.dir_list:
                warnings.warn(f"Stock '{label.upper()}' is not in data library. Use StockData.add('{label}') to add the stock to the library.")
                continue
            
            # Construct the local data folder.
            path = self.create_folder_path(label.lower())
            
            # Load current data.
            with open(f"{path}/meta.pkl", "wb") as fp:
                meta = pickle.load(fp)
            data = pd.read_pickle(f"{path}/data.pkl")
            last_date = meta['last_date']
            
            # Update data.
            tckr = yf.Ticker(label.upper())
            new_data = add_columns_on_import(add_tckr.history(start=last_date))
            
            # Add new date to old data.
            data = pd.concat([data, new_data], axis=0).drop_duplicates()
            data.to_pickle(f"{path}/data.pkl")
            meta['last_date'] = f"{str(data['Date'].max().year)}-{str(data['Date'].max().month).zfill(2)}-{str(data['Date'].max().day).zfill(2)}"
            with open(f"{path}/meta.pkl", "wb") as fp:
                pickle.dump(meta, fp, protocol=pickle.HIGHEST_PROTOCOL)


    def add_and_update(self, labels):
        """
        Updates existing data and adds data for new symbols.
        
        Args:
            Args:
            labels (str, list): A single string or list of strings
             of the symbols indicating the stock or stocks to be
             updated or added. Default is None, which only updates
             the existing stocks found in the directory.
        """
        labels = check_and_convert_value_to_list(labels, str)
        add_labels, update_labels = [], []
        for label in labels:
            if label.lower() in self.dir_list:
                update_labels.append(label.lower())
            else:
                add_labels.append(label.lower())
        
        # Add and update.
        self.update(labels=update_labels)
        self.add(labels=add_labels)


    def load(self, labels=None):
        """
        Load data from the data folder into the StockData object. Data is loaded
        into a dictionary of pandas.DataFrames.
        
        Args:
            labels (str, list): A single string or list of strings
             of the symbols indicating the stock or stocks to be
             loaded. Default is None, which will load all stock data
             found in the data directory.
        """
        # Initialize empty container.
        self.d_data = {}
        
        # Handle default case.
        if isinstance(labels, type(None)):
            labels = [l.lower() for l in self.dir_list]
        else:
            labels = check_and_convert_value_to_list(labels, str)
        
        # Loop and populate object data.
        for label in labels:
            # Ensure data is in library, instruct otherwise.
            if label.lower() not in self.dir_list:
                print(f"No stock data found for '{label.upper()}'. Use the '.add()' method to add a new stock symbol.")
                continue
            self.d_data[label.lower()] = pd.read_pickle(self.create_folder_path(label.lower())+"/data.pkl")


    def get_object_data(self):
        """
        Returns the dictionary containing all object data.
        """
        try:
            return self.d_data
        except:
            print("StockData object does not has any data loaded.")


    def add_moving_average(self, labels=None, column='Close', windows=None, method='sma'):
        """
        Calculates the moving average for a given label and column.
        Columns are added to each stock DataFrame as SMAX or EMAX,
        where X is the window size in days.
        
        Args:
            labels (str, list): A single string or list of strings
             of the symbols indicating the stock or stocks to have 
             the moving average calculated. Default is None, which
             will calculate the moving average for all labels.
            
            column (str): The column from the stock DataFrame to use
             to calculate the moving average. Accepted values are 'Open',
             'Close', 'High', 'Low'.
            
            windows (int, list): The window for moving average calculated, in days.
             If a list is provided, moving averages will be calculated
             for each of them.
            
            method (str): Type of moving average to calculate. Accepted values
             are 'sma' (simple moving average), 'ema' (exponential moving
             average). Default is 'ema'.
        """
        # Handle errors.
        if not self.d_data:
            raise ValueError("There is no data loaded into this StockData object.")
        if isinstance(windows, type(None)):
            raise ValueError("At least one value must be passed to argument 'windows'.")
        if method not in ['sma', 'ema']:
            raise ValueError("Argument 'method' must be one of: 'sma', 'ema'.")
        
        # Handle default case.
        if isinstance(labels, type(None)):
            labels = [l.lower() for l in self.dir_list]
        else:
            labels = check_and_convert_value_to_list(labels, str)
        
        # Handle moving averages.
        d_ma = {'sma': simple_moving_average,
                'ema': exp_moving_average}
        for label in labels:
            self.d_data[label] = d_ma[method](self.d_data[label], column, windows)


    def add_macd(self, labels=None):
        """
        Adds the MACD and 12- and 26-period EMA to each stock symbol data.
        
        Args:
            labels (str, list): A single string or list of strings
             of the symbols indicating the stock or stocks to have 
             the moving average calculated. Default is None, which
             will calculate the moving average for all labels.
        """
        # Handle default case.
        if isinstance(labels, type(None)):
            labels = [l.lower() for l in self.dir_list]
        else:
            labels = check_and_convert_value_to_list(labels, str)
        
        for label in labels:
            self.d_data[label] = macd(self.d_data[label], 'Close')
