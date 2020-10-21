import yfinance as yf
import pandas as pd

def PreInfo(stock_symbol):
    try:
        lookup_stock = yf.Ticker(stock_symbol)
        return [lookup_stock.info]
    except:
        return None

def Information(stock_symbol, period="1y"):
    try:
        global stock
        stock = yf.Ticker(stock_symbol)
        global stock_info, df_stock_history
        stock_info = stock.info
        df_stock_history = stock.history(period)
        return [stock_info, df_stock_history]
    except:
        return None

def PerformancePlot():
    try: 
        pass
    except:
        pass

def Recommendation():
    df_recommendations = stock.recommendations
    print(df_recommendations)

def Sustainability():
    df_sustainability = stock.sustainability
    return df_sustainability