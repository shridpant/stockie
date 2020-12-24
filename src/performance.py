# MIT License

# Copyright (c) 2020 Shrid Pant

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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