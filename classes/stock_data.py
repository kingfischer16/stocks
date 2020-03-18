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
        labels = labels if isinstance(labels, list) else [labels]
        
        # Loop and add data.
        for label in labels:
            # Warn if the label exists.
            if label in self.dir_list:
                warnings.warn(f"Stock '{label.upper()}' is currently in the data library. Use StockData.update('{label}') to update the stock data.")
                continue
            
            # Construct the local data folder.
            path = self.create_folder_path(label)
            
            # Download data.
            tckr = yf.Ticker(label.upper())
            data = tckr.history(period='max').reset_index()
            meta = {
                'symbol': label.upper(),
                'last_date': f"{data['Date'].max().year}-{data['Date'].max().month.zfill(2)}-{data['Date'].max().day.zfill(2)}"
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
            labels = labels if isinstance(labels, list) else [labels]
        
        # Loop and udpate data.
        for label in labels:
            # Warn if the label does not currently exist.
            if label not in self.dir_list:
                warnings.warn(f"Stock '{label.upper()}' is not in data library. Use StockData.add('{label}') to add the stock to the library.")
                continue
            
            # Construct the local data folder.
            path = create_folder_path(label)
            
            # Load current data.
            with open(f"{path}/meta.pkl", "wb") as fp:
                meta = pickle.load(fp)
            data = pd.read_pickle(f"{path}/data.pkl")
            last_date = meta['last_date']
            
            # Update data.
            tckr = yf.Ticker(label.upper())
            new_data = tckr.history(start=last_date).reset_index()
            data = pd.concat([data, new_data], axis=0).drop_duplicates()
            data.to_pickle(f"{path}/data.pkl")
            meta['last_date'] = f"{data['Date'].max().year}-{data['Date'].max().month.zfill(2)}-{data['Date'].max().day.zfill(2)}"
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
        labels = labels if isinstance(labels, list) else [labels]
        add_labels, update_labels = [], []
        for label in labels:
            if label.lower() in self.dir_list:
                update_labels.append(label.lower())
            else:
                add_labels.append(label.lower())
        
        # Add and update.
        self.update(labels=update_labels)
        self.add(labels=add_labels)
