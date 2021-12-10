import numpy as np
import pandas as pd
import requests
import xlsxwriter
import math
import secret

__author__ = "Ejie Emmanuel Ebuka"

# Equal-Weight S&P 500 Screener

stocks = pd.read_csv('data/sp500_csv.csv')
public_key = secret.__SANDBOX_IEX_PK
private_key = secret.__SANDBOX_IEX_SK

symbol = "AAPL"
api_url = f"https://sandbox.iexapis.com/stable/stock/{symbol}/quote/?token={private_key}"
data = requests.get(api_url).json()
price = data['latestPrice']
marketcap = data['marketCap']
cols = ['Ticker', 'Stock Price', 'Market Capitalization', 'Number of shares to Buy']
final_dataframe = pd.DataFrame(columns=cols)

final_dataframe.append(
    pd.Series(
        [
            symbol,
            price,
            marketcap,
            "N/A"
        ],
        index=cols,
    ),
    ignore_index=True
)

# Using stocks in our s&p 500 csv data to generate data frame
for stock in stocks['Symbol'][:10]:
    api_url = f"https://sandbox.iexapis.com/stable/stock/{stock}/quote/?token={private_key}"
    data = requests.get(api_url).json()
    final_dataframe = final_dataframe.append(
        pd.Series(
            [
                stock,
                price,
                marketcap,
                "N/A"
            ],
            index=cols,
        ),
        ignore_index=True
    )

# Using batch api caalls to improve our stocks performance
# Batc api calls are one of the easiest ways to improve the performance of your code.

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

symbol_groups = list(chunks(stocks['Symbol'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]) )
# print(symbol_strings[i])
final_dataframe = pd.DataFrame(columns = cols)
for symbol in symbol_strings:
    batch_api_url = f'https://sandbox.iexapis.com/stable//stock/market/batch?symbols={symbol}&types=quote&token={private_key}'
    data = requests.get(batch_api_url).json()
    for sym in symbol.split(','):
        final_dataframe = final_dataframe.append(
            pd.Series(
                [
                    sym,
                    data[sym]['quote']['latestPrice'],
                    data[sym]['quote']['marketCap'],
                    'N/A'
                ],
                index = cols
            ),
            ignore_index = True
        )

# Calculate the number of share to buy using the current stock price
portfolio_size = int(input("Enter the value of your portfolio: "))

try:
    value = float(portfolio_size)
    print(value)
except ValueError:
    print(f"That is not a number!\nPlease, enter an integer!")
    value = float(portfolio_size)
    print(value)

position_size = value / len(final_dataframe.index)
for i in range(0, len(final_dataframe.index)):
    final_dataframe.loc[i, 'Number of shares to Buy'] = math.floor(position_size / final_dataframe.loc[i, 'Stock Price'])
print(final_dataframe)

# Formatting our output into excel
excel_writer = pd.ExcelWriter('data/buy.xlsx', engine = "xlsxwriter")
final_dataframe.to_excel(excel_writer, "buy", index = False)
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

# excel_writer.sheets["buy"].set_column('A:A', # This tells the method to apply the format to col A
#                                       18, # This tells the method to apply a column width of 18
#                                       string_f # This applies the format "string_tamplate"
#                                       )
# excel_writer.sheets["buy"].set_column('B:B', # This tells the method to apply the format to col B
#                                       18, # This tells the method to apply a column width of 18
#                                       string_f # This applies the format "string_tamplate"
#                                       )
# excel_writer.sheets["buy"].set_column('C:C', # This tells the method to apply the format to col C
#                                       18, # This tells the method to apply a column width of 18
#                                       string_f # This applies the format "string_tamplate"
#                                       )
# excel_writer.sheets["buy"].set_column('D:D', # This tells the method to apply the format to col D
#                                       18, # This tells the method to apply a column width of 18
#                                       string_f # This applies the format "string_tamplate"
#                                       )
# excel_writer.save()

excel_writer.sheets['buy'].write("A1", "Ticker", string_f)
excel_writer.sheets['buy'].write("B1", "Stock Price", dollar_f)
excel_writer.sheets['buy'].write("C1", "Market Capitalization", dollar_f)
excel_writer.sheets['buy'].write("D1", "Number of shares to Buy", integer_f)

column_f = {
    "A" : ["Ticker", string_f],
    "B" : ["Stock Price", dollar_f],
    "C" : ["Market Capitalization", dollar_f],
    "D" : ["Number of shares to Buy", integer_f]
}
for column in column_f.keys():
    excel_writer.sheets['buy'].set_column(f'{column}:{column}', 18, column_f[column][1])
    excel_writer.sheets['buy'].write(f"{column}1", column_f[column][0], column_f[column][1])
excel_writer.save()