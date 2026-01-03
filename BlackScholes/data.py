import yfinance as yf
import pandas as pd

def get_stock_price(ticker: str, start: str = None, end: str = None) -> float:
    #fetches most recent closing price for ticker
    try:
        stock = yf.Ticker(ticker)

        if start and end:
            hist = stock.history(start=start, end=end)
        else:
            #fetch most recent day by default
            hist = stock.history(period="1d")
        
        if hist.empty:
            raise ValueError(f"No data available for ticker {ticker }")
        return hist["Close"].iloc[-1]
    
    except Exception as e:
        print(f"Error fetching stock prices for ticker {ticker}")
        return None



