import pandas as pd
import pypfopt
from pypfopt import risk_models
from pypfopt import EfficientFrontier
from pypfopt import expected_returns

RISKFREE_RATE = 0.03

prices = pd.read_csv("data/return_df.csv", index_col="Date")

# Calculate expected returns and sample covariance
mu = expected_returns.mean_historical_return(prices)
S = risk_models.CovarianceShrinkage(prices).ledoit_wolf()

# Optimize for maximal Sharpe ratio, which is the tangential portfolio
ef = EfficientFrontier(mu, S)
raw_weights = ef.max_sharpe(RISKFREE_RATE)
cleaned_weights = ef.clean_weights()
ef.save_weights_to_file("data/weights.csv")  # saves to file
print(cleaned_weights)

ef.portfolio_performance(verbose=True, risk_free_rate=RISKFREE_RATE)

