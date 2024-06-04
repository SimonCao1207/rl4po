import numpy as np
import pandas as pd
from settings import *

DAILY_RISK_FREE = (1 + RISKFREE_RATE) ** (1/252) - 1 # APPROXIMATION, to 252 days a year

def get_daily_return (weight_df):
    price = pd.read_csv('./data/return_df.csv', index_col='Date')

    assert np.all(price.columns == mvo_weight.columns)

    w = np.zeros(weight_df.shape[1])
    port = np.zeros(weight_df.shape[1])
    cash = 1

    ret = []
    for index, row in weight_df.iterrows():
        p = price.loc[index].to_numpy()

        port_value = np.dot(port, p) + cash * (1 + DAILY_RISK_FREE)

        w = row.to_numpy()
        exp = w * port_value
        cash = (1 - np.sum(w)) * port_value
        port = exp / p

        if port_value > 5: exit()

        ret.append(port_value)

    return pd.DataFrame(ret, index=price.index[price.index > TEST_START_DATE], columns=['port_value']) # type: ignore

if __name__ == "__main__":
    mvo_weight = pd.read_csv('./data/mvo.csv', index_col='Date')
    mvo_daily_return = get_daily_return(mvo_weight)
    mvo_daily_return.to_csv('./data/mvo_analysis.csv')


