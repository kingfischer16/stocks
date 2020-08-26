"""
# ============================================================================
# SCRAPING_UTILS.PY
# ----------------------------------------------------------------------------
# Utility functions that involve scraping websites and web APIs.
#
# ============================================================================
"""

# Imports
import re, requests
import yfinance as yf
from edgar import Company, XBRL, XBRLElement, Edgar


def get_name_and_cik(tickers):
    """
    Gets the company names and CIK numbers given the ticker
    symbol or list of symbols.
    
    Args:
        tickers (str, list): A ticker symbol or list of ticker symbols.
    
    Returns:
        (dict): A dict of tuples of the form 'Ticker': ('Company Name', 'CIK#')
    """
    tickers = [tickers] if not isinstance(tickers, list) else tickers
    tickers = [ticker.upper() for ticker in tickers]
    
    SEC_URL = 'http://www.sec.gov/cgi-bin/browse-edgar?CIK={}&Find=Search&owner=exclude&action=getcompany'
    CIK_RE = re.compile(r'.*CIK=(\d{10}).*')    
    cik_dict = {}
    
    for ticker in tickers:
        yf_name = yf.Ticker(ticker).info['longName']
        f = requests.get(SEC_URL.format(ticker), stream = True)
        results = CIK_RE.findall(f.text)
        if len(results):
            results[0] = int(re.sub(r'\.[0]*', '.', results[0]))
            cik_dict[ticker] = (yf_name, str(results[0]))
    
    return cik_dict

