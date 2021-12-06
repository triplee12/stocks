# Algorithi=mic Trading

- Algorithmic trading is using computers to make investment decisions.

Threr are many different types of algorithmic trading. The main difference is their speed of execution.

## The Algorithmic Trading Landscape

- Here are some of the main players in the algorithmic trading landscape:

1. Renaissance Technologies: $165b in AUM
2. AQR Capital Management: 61b in AUM
3. Citadel Securities: 32b in AUM

## Algorithmic Trading And Python

- Python is the most popular programming language for algorithmic trading.

However, Python is slow. This means that it is often used as a "glue language" to trigger code that runs in other languages.

One of examples of this is the NumPy library for Python, which we'll be using in this course.

NumPy is the most popular Python library for performing numerical computing.

- The process of running a quntitative investing strategy can be broken down into the following steps:

1. Collect data
2. Develop a hypothensis for a strategy
3. Backtest that strategy
4. Implement the strategy in production

### This Is An Introductory Course, It Will Differ From production Algorithmic Trading In 3 Ways

1. We will be using random data
2. We will not be executing trades
3. We will be saving trades in cv files

## API Basics And Configuration

- What is an API?
An API is an Application Programming Interface.

- In this course, we will be using the IEX Cloud API to gather stock market data to make investment decisions.
- GET Request: Request data from IEX Cloud API database.
- POST Request: Adds data to the database exposed by the API (Create only).
- PUT: Adds and overwrites data in the database exposed by the API (Create or Replace).
- DELETE Request: Deletes data from the API's database

Link for free APIs on github : <https://github.com/public-apis/public-apis> for best practice on apis

## Project 1

- Equal-Weight S and P 500 Screener
The S&P 500 is the world's most popular stock market index.

Many investment funds are benchmarked to the S&P 500. This means that they seek to replicate the performance of this index by owning all the stocks that are held in the index.
One of the most important characteristics of thr S&P 500 is that it is market capitalizarion-weighted.

In this first project, you will build an alternative version of the S&P 500 Indexer and where each company has the same weighting.

## Project 2

- Quantitative Momentum Screener
Momentum investing means investing in assests that have increased in price the most.
Example:
Imagine that you have the choice between investing in two stocks that have had the following returns over the last year:
- Apple (AAPL): 35%
- Microsoft (MSFT): 20%
A momentum investing strategy would suggest investing in Apple because of its higher recent price return.

There are many other naunces to momentum investing strategies that we will explore throughout this course.

## Project 3

- Quantitative Value Screener
Value investing means investing in stocks that are trading below their perceived intrinsic value.

Value investing was popularized by investors like Seth Klarman, Warren Buffett and Benjamin Graham.
Creating algorithmic value investing strategies relies on a concept called multiples.

Multiples are calculated by dividing a company's stock price by some measures of the company's worth like earnings or assests.

Examples of common multiples used in value investing:

- Price to earnings
- Price to book value
- Price to free cash flow

Each of the individual multiples used by value investors has its pros and cons.
One way to minimize the impact of any specific multiple is by using a composite.

We will use a composite of 5 different value prices in our strategy.
