import numpy as np
import pandas as pd
from settings import *
import quantstats as qs
import matplotlib.pyplot as plt

DAILY_RISK_FREE = (1 + RISKFREE_RATE) ** (1/252) - 1 # APPROXIMATION, to 252 days a year

def get_daily_return (weight_df):
    price = pd.read_csv('./data/return_df.csv', index_col='Date', parse_dates=['Date'])

    assert np.all(price.columns == mvo_weight.columns)

    w = np.zeros(weight_df.shape[1])
    port = np.zeros(weight_df.shape[1])
    cash = 1

    port_val = []
    ret = []
    for index, row in weight_df.iterrows():
        p = price.loc[index].to_numpy()

        port_value = np.dot(port, p) + cash * (1 + DAILY_RISK_FREE)

        w = row.to_numpy()
        exp = w * port_value
        cash = (1 - np.sum(w)) * port_value
        port = exp / p

        if port_value > 5: exit()

        if len(port_val) == 0: 
            ret.append(port_value - 1)
        else: 
            ret.append(port_value - port_val[-1])
        port_val.append(port_value)
        
    return pd.DataFrame(
        np.array([ret, port_val]).T, 
        index=price.index[(price.index >= TEST_START_DATE) & (price.index <= TEST_END_DATE)], 
        columns=['return', 'port_value']                        # type: ignore
    ) 

if __name__ == "__main__":
    mvo_weight = pd.read_csv('./results_mvo/10-mvo_trim.csv', index_col='Date', parse_dates=['Date'])
    mvo_daily_return = get_daily_return(mvo_weight)
    mvo_daily_return.to_csv('./results_mvo/10-mvo_analysis.csv')

    mvo = mvo_daily_return['return']
    qs.reports.html(mvo, output="./mvo.html")

    rl_result = pd.read_csv('./results_rl/df_account_value_ensemble.csv', index_col='date', parse_dates=['date'])
    rl = rl_result['daily_return']

    qs.reports.html(rl, benchmark=mvo, output="./compare.html")

