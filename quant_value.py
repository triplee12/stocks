import numpy as np
import pandas as pd
import requests
import math
from scipy import stats
import xlsxwriter
import secret
from statistics import mean


__author__ = "Ejie Emmanuel Ebuka"

# Quantitative Value Screener

"""
Quantitative Value Screener
Value investing means investing in stocks that are trading below their perceived intrinsic value.
"""

private = secret.__SANDBOX_IEX_SK
stocks = pd.read_csv('data/sp500_csv.csv')
symbol = "AAPL"
api_url = f"https://sandbox.iexapis.com/stable/stock/{symbol}/quote?token={private}"
data = requests.get(api_url).json()
price = data['latestPrice']

# Using batch api call
def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

symbol_groups = list(chunks(stocks['Symbol'], 50))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]) )
cols = ['Ticker', 'Price', 'Price-to-Earnings Ratio', 'Number of shares to Buy']
final_dataframe = pd.DataFrame(columns = cols)
for syb_s in symbol_strings:
    batch_api_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={syb_s}&types=quote&token={private}'
    data = requests.get(batch_api_url).json()
    for syb in syb_s.split(','):
        final_dataframe = final_dataframe.append(
            pd.Series(
                [
                    syb,
                    data[syb]['quote']['latestPrice'],
                    data[syb]['quote']['peRatio'],
                    "N/A"
                ],
                index = cols
            ),
            ignore_index = True
        )

# Removing glamour stocks
# The opposite of a "value stock" is a "glamour stock"
final_dataframe.sort_values('Price-to-Earnings Ratio', ascending=False, inplace=True)
final_dataframe[final_dataframe['Price-to-Earnings Ratio'] > 0]
final_dataframe = final_dataframe[:100]
final_dataframe.reset_index(inplace=True)
final_dataframe.drop('index', axis=1, inplace=True)

# Calculate Number of Shares to Buy
def portfolio():
    global portfolio_size
    portfolio_size = int(input("Enter the size of your portfolio: "))
    try:
        float(portfolio_size)
    except ValueError:
        print("That is not an integer! \nPlease try again.")
        portfolio_size = int(input("Enter the size of your portfolio: "))

portfolios = portfolio()
amount_to_buy = float(portfolio_size)/len(final_dataframe.index)
# loop over the final_dataframe to calculate each stock
for i in range(0, len(final_dataframe.index)):
    final_dataframe.loc[i, 'Number of shares to Buy'] = math.floor(amount_to_buy/ final_dataframe.loc[i, 'Price'])

# Building a better and more realistic value strategy
"""
Every valuation metric has certain flaws.
For example, the price-to-earnings ratio does not work well with stocks with nagetive earnings.
Investors typically use a composite basket of valuation metrics to build robust quantitative value strategy.
We will filter stocks with lowest percentile on the following metrics:
- Price-to-earnings ratio
- Price-to-book ratio
- Price-to-sales ratio
- Enterprise Value divided by Earnings Before interest, Taxes, Depreciation and Amorntization (EV/EBITDA)
- Enterprise Value divided by Gross Profit (EV/GP)
Some of these metrics are not provided directly by the IEX Cloud API and, must be computed after pulling raw data.
We will start from scratch.

"""

batch_api_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol}&types=quote,advanced-stats&token={private}'
data = requests.get(batch_api_url).json()

# Price-to-earnings ratio
pe_ratio = data[symbol]['quote']['peRatio']
# Price-to-book ratio
pb_ratio = data[symbol]['advanced-stats']['priceToBook'] 
# Price-to-sales ratio
ps_ratio = data[symbol]['advanced-stats']['priceToSales']
# Enterprise Value divided by Earnings Before interest, Taxes, Depreciation and Amorntization (EV/EBITDA)
enterprise_value = data[symbol]['advanced-stats']['enterpriseValue']
ebitda = data[symbol]['advanced-stats']['EBITDA']
ev_to_ebitda = enterprise_value / ebitda
# Enterprise Value divided by Gross Profit (EV/GP)
gross_profit = data[symbol]['advanced-stats']['grossProfit']
ev_to_gross_profit = enterprise_value / gross_profit

# DataFrame
rvp_columns = [
    'Ticker',
    'Price',
    'Price-to-Earnings Ratio',
    'PE Percentile',
    'Number of shares to Buy',
    'Price-to-Book ratio',
    'PB Percentile',
    'Price-to-Sales ratio',
    'PS Percentile',
    'EV/EBITDA',
    'EV/EBITDA Percentile',
    'EV/GP',
    'EV/GP Percentile',
    'RV Score'
]
rv_dataframe = pd.DataFrame(columns = rvp_columns)
for sym_s in symbol_strings:
    batch_api_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={sym_s}&types=quote,advanced-stats&token={private}'
    data = requests.get(batch_api_url).json()
    for sym in sym_s.split(','):
        enterprise_value = data[sym]['advanced-stats']['enterpriseValue']
        ebitda = data[sym]['advanced-stats']['EBITDA']
        gross_profit = data[sym]['advanced-stats']['grossProfit']
        # ev_to_ebitda
        try:
            ev_to_ebitda = enterprise_value / ebitda
        except TypeError:
            ev_to_ebitda = np.NaN
        # ev_to_gross_profit
        try:
            ev_to_gross_profit = enterprise_value / gross_profit
        except TypeError:
            ev_to_gross_profit = np.NaN
        rv_dataframe = rv_dataframe.append(
            pd.Series(
                [
                    sym,
                    data[sym]['quote']['latestPrice'],
                    data[sym]['quote']['peRatio'],
                    'N/A',
                    'N/A',
                    data[sym]['advanced-stats']['priceToBook'],
                    'N/A',
                    data[sym]['advanced-stats']['priceToSales'],
                    'N/A',
                    ev_to_ebitda,
                    'N/A',
                    ev_to_gross_profit,
                    'N/A',
                    'N/A'
                ],
                index = rvp_columns
            ),
            ignore_index = True
        )

# Dealing with missing data in our dataframe
rv_dataframe[rv_dataframe.isnull().any(axis=1)]
# There are two main approaches:
# 1 Drop missing data from data set using pandas 'dropna' method
# 2 Replace missing data with a new value using pandas 'fillna' method
# We will use fillna method
for col in ['Price-to-Earnings Ratio', 'Price-to-Book ratio', 'Price-to-Sales ratio', 'EV/EBITDA', 'EV/GP']:
    rv_dataframe[col].fillna(rv_dataframe[col].mean())
    rv_dataframe[rv_dataframe.isnull().any(axis=1)]

# Calculate 
# 'Price to Earnings Ratio',
# 'PE Percentile',
# 'Number of shares to Buy',
# 'Price-to-Book ratio',
# 'PB Percentile',
# 'Price-to-Sales ratio',
# 'PS Percentile',
# 'EV/EBITDA',
# 'EV/EBITDA Percentile',
# 'EV/GP',
# 'EV/GP Percentile'

metrics = {
    'Price-to-Earnings Ratio' : 'PE Percentile',
    'Price-to-Book ratio' : 'PB Percentile',
    'Price-to-Sales ratio' : 'PS Percentile',
    'EV/EBITDA' : 'EV/EBITDA Percentile',
    'EV/GP' : 'EV/GP Percentile'
}
for metric in metrics.keys():
    for row in rv_dataframe.index:
        rv_dataframe.loc[row, metrics[metric]] = stats.percentileofscore(rv_dataframe[metric], rv_dataframe.loc[row, metric])

# Calculating the RV score
for row in rv_dataframe.index:
    value_percen = []
    for metric in metrics.keys():
        value_percen.append(rv_dataframe.loc[row, metrics[metric]])
    rv_dataframe.loc[row, 'RV Score'] = mean(value_percen)

# Recommending the Best 50 Value Stocks
rv_dataframe.sort_values('RV Score', ascending=True, inplace=True)
rv_dataframe = rv_dataframe[:50]
rv_dataframe.reset_index(drop=True, inplace=True)

# Calculating the number of shares to buy
portfolios = portfolio()
amount_to_buy = float(portfolio_size)/len(rv_dataframe.index)
for i in rv_dataframe.index:
    rv_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(amount_to_buy/rv_dataframe.loc[i, 'Price'])
print(rv_dataframe)

# Format our excel data
excel_writer = pd.ExcelWriter('data/quant_value.xlsx', engine="xlsxwriter")
rv_dataframe.to_excel(excel_writer,sheet_name="Quantitative Value Strategy Screener", index = False)
# create a formatting
# Format
bg_color = "#aaa"
font_color = "#00ffaa"

string_f = excel_writer.book.add_format(
    {
        "bg_color" : bg_color,
        "font_color" : font_color,
        "border" : 2
    }
)

float_f = excel_writer.book.add_format(
    {
        'num_format': '0',
        "bg_color" : bg_color,
        "font_color" : font_color,
        "border" : 2
    }
)

integer_f = excel_writer.book.add_format(
    {
        "num_format" : "0",
        "bg_color" : bg_color,
        "font_color" : font_color,
        "border" : 2
    }
)

dollar_f = excel_writer.book.add_format(
    {
        "num_format" : "$0.00",
        "bg_color" : bg_color,
        "font_color" : font_color,
        "border" : 2
    }
)

percent_f = excel_writer.book.add_format(
    {
        "num_format" : "0.0%",
        "bg_color" : bg_color,
        "font_color" : font_color,
        "border" : 2
    }
)

column_f = {
    "A" : ["Ticker", string_f],
    "B" : ["Price", dollar_f],
    "C" : ["Number of shares to Buy", integer_f],
    "D" : ['Price-to-Earnings Ratio', float_f],
    "E" : ['PE Percentile', percent_f],
    "F" : ['Price-to-Book ratio', float_f],
    "G" : ['PB Percentile', percent_f],
    "H" : ['Price-to-Sales ratio', float_f],
    "I" : ['PS Percentile', percent_f],
    "J" : ['EV/EBITDA', string_f],
    "K" : ['EV/EBITDA Percentile', percent_f],
    "L" : ['EV/GP', float_f],
    "M" : ['EV/GP Percentile', percent_f],
    "N" : ['RV Score', percent_f]
}
for coln in column_f.keys():
    excel_writer.sheets["Quantitative Value Strategy Screener"].set_column(f'{coln}:{coln}', 22, column_f[coln][1])
    excel_writer.sheets["Quantitative Value Strategy Screener"].write(f"{coln}1", column_f[coln][0], column_f[coln][1])
excel_writer.save()
