from collections import OrderedDict
import numpy as np
import pandas as pd
from pypfopt import risk_models, EfficientFrontier, expected_returns
from settings import *

def tangential_port (test_index) :

    prices = pd.read_csv("data/return_df.csv")
    prices = prices.loc[:test_index]
    prices = prices.drop('Date', axis=1)

    # Calculate expected returns and sample covariance
    mu = expected_returns.mean_historical_return(prices)
    S = risk_models.CovarianceShrinkage(prices).ledoit_wolf()

    # Optimize for maximal Sharpe ratio, which is the tangential portfolio
    ef = EfficientFrontier(mu, S)
    ef.max_sharpe(RISKFREE_RATE)
    cleaned_weights = ef.clean_weights()

    ret, vol, _ = ef.portfolio_performance(risk_free_rate=RISKFREE_RATE)

    # no shorting kelly
    kelly = max(min((ret - RISKFREE_RATE) / vol, 1), 0) # type: ignore

    cleaned_weights = OrderedDict((key, kelly * cleaned_weights[key]) for key in cleaned_weights) # type: ignore

    return cleaned_weights

def row_propagate (weight) :
    last_row = None
    for i in range(len(weight)) :
        if np.isnan(weight.iloc[i,1]): 
            if last_row is None : 
                raise Exception("First row must not be NaN")
            weight.iloc[i,1:] = last_row.iloc[1:]
        last_row = weight.iloc[i]
    return weight


def index_of_rebalancing_dates (freq) : 
    prices = pd.read_csv('data/return_df.csv')
    date = prices[['Date']]
    last_index = date.iloc[-1].name
    date = date[date['Date'] >= TEST_START_DATE]
    first_index = date.iloc[0].name # type: ignore
    return range(first_index, last_index, freq)


if __name__ == "__main__" :
    weight = pd.read_csv('data/return_df.csv')
    weight = weight[weight['Date'] >= TEST_START_DATE]
    weight.iloc[:,1:] = np.nan
    
    indices = index_of_rebalancing_dates(MVO_REBALANCE_FREQ)
    for i in indices: 
        w = tangential_port(i)
        for tick in w: 
            weight.loc[i, tick] = w[tick]

    weight = row_propagate(weight)
    weight.set_index('Date', inplace=True)
    weight.to_csv('./data/mvo.csv')
    print("weight saved to mvo.csv")
