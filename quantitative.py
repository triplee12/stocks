import numpy as np
import pandas as pd
import requests
import math
from scipy import stats
import xlsxwriter
import secret
from statistics import mean

__author__ = "Ejie Emmanuel Ebuka"

# Quantitative Momentum Screener
"""
Momentum investing means investing in the stocks that have increased in price the most.

And for this project we are going to build an investing strategy that selects the 50 stocks with the highest price momentum.
Drom there, we will calculate recommended trades for an equal-weight portfolio of these 50 stocks.
"""
private = secret.__SANDBOX_IEX_SK
stocks = pd.read_csv('data/sp500_csv.csv')
symbol = "AAPL"
api_url = f"https://sandbox.iexapis.com/stable/stock/{symbol}/stats?token={private}"
data = requests.get(api_url).json()

# Parsing api call
data["year1ChangePercent"]

# Using batch api call
def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

symbol_groups = list(chunks(stocks['Symbol'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]) )
cols = ['Ticker', 'Price', 'One-Year Price Return', 'Number of shares to Buy']
final_dataframe = pd.DataFrame(columns = cols)

# We need each stock symbol
for sym in symbol_strings:
    batch_api_url = f'https://sandbox.iexapis.com/stable//stock/market/batch?symbols={sym}&types=price,stats&token={private}'
    data = requests.get(batch_api_url).json()
    for sy in sym.split(','):
        final_dataframe = final_dataframe.append(
            pd.Series(
                [
                    sy,
                    data[sy]['price'],
                    data[sy]['stats']['year1ChangePercent'],
                    "N/A"
                ],
                index = cols
            ),
            ignore_index = True
        )

# Remove low-momentum stocks
final_dataframe.sort_values('One-Year Price Return', ascending=False, inplace=True) # Sort by one year price return
final_dataframe = final_dataframe[:50] # first 50 stocks with high price return
final_dataframe.reset_index(drop= True, inplace = True) # Reset index of final_dataframe

# Calculate number of shares to buy using stock one-year price return
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
# print(final_dataframe)

# Building momentum strategy
# High quality momentum stocks
high = [
    'Ticker',
    'Price',
    'Number of Shares to Buy',
    'One-Year Price Return',
    'One-Year Return Percentile',
    'Six-Month Price Return',
    'Six-Month Return Percentile',
    'Three-Month Price Return',
    'Three-Month Return Percentile',
    'One-Month Price Return',
    'One-Month Return Percentile',
    'HQM Score'
]
# create high momentum dataframe
hgm_dataframe = pd.DataFrame(columns=high)

# loop over stocks symbols
for symb in symbol_strings:
    batch_api_url = f'https://sandbox.iexapis.com/stable//stock/market/batch?symbols={symb}&types=price,stats&token={private}'
    data = requests.get(batch_api_url).json()
    for sym in symb.split(','):
        hgm_dataframe = hgm_dataframe.append(
            pd.Series(
                [
                    sym,
                    data[sym]['price'],
                    'N/A',
                    data[sym]['stats']['year1ChangePercent'],
                    'N/A',
                    data[sym]['stats']['month6ChangePercent'],
                    'N/A',
                    data[sym]['stats']['month3ChangePercent'],
                    'N/A',
                    data[sym]['stats']['month1ChangePercent'],
                    'N/A',
                    'N/A'
                ],
                index = high
            ),
            ignore_index = True
        )

# Calculating momentum percentile
periods = [
    'One-Year',
    'Six-Month',
    'Three-Month',
    'One-Month'
]
# Loop over the percentiles with the period
for row in hgm_dataframe.index:
    for time in periods:
        col = f'{time} Price Return'
        percentile = f'{time} Return Percentile'
        hgm_dataframe.loc[row, percentile] = stats.percentileofscore(hgm_dataframe[col], hgm_dataframe.loc[row, col]) / 100

# Calculating the High Quality Momentum score
# The arithmetic mean of the 4 momentum percentile scores
# Create a loop
for row in hgm_dataframe.index:
    mom_percentile = []
    for time in periods:
        mom_percentile.append(
            hgm_dataframe.loc[row, f'{time} Return Percentile']
        )
    hgm_dataframe.loc[row, 'HQM Score'] = mean(mom_percentile)
print(hgm_dataframe)

# Selecting the best momentum stocks
# Using sort_values method
hgm_dataframe.sort_values('HQM Score', ascending=False, inplace=True)
hgm_dataframe.reset_index(drop = True, inplace = True)


# Calculating the number of shares to buy
portfolios = portfolio()
amount_to_buy = float(portfolio_size)/len(hgm_dataframe.index)
for i in hgm_dataframe.index:
    hgm_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(amount_to_buy/hgm_dataframe.loc[i, 'Price'])
print(hgm_dataframe)

# Format our excel data
excel_writer = pd.ExcelWriter('data/quantative.xlsx', engine="xlsxwriter")
hgm_dataframe.to_excel(excel_writer,sheet_name="Momentum Strategy Screener", index = False)
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
    "D" : ['One-Year Price Return', dollar_f],
    "E" : ['One-Year Return Percentile', percent_f],
    "F" : ['Six-Month Price Return', dollar_f],
    "G" : ['Six-Month Return Percentile', percent_f],
    "H" : ['Three-Month Price Return', dollar_f],
    "I" : ['Three-Month Return Percentile', percent_f],
    "J" : ['One-Month Price Return', dollar_f],
    "K" : ['One-Month Return Percentile', percent_f],
    "L" : ['HQM Score', integer_f]
}
for coln in column_f.keys():
    excel_writer.sheets['Momentum Strategy Screener'].set_column(f'{coln}:{coln}', 22, column_f[coln][1])
    excel_writer.sheets['Momentum Strategy Screener'].write(f"{coln}1", column_f[coln][0], column_f[coln][1])
excel_writer.save()
