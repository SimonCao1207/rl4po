import os
import json
import yfinance as yf
import pandas as pd
import datetime

start_date = "2006-01-01"
end_date = "2021-12-31"

# def get_sp_data():
#     sp_assets = pd.read_html(
#         'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
#     assets = sp_assets['Symbol'].str.replace('.', '-').tolist()
#     data = yf.download(assets, start=start_date, end=end_date)

#     df_reset = data.reset_index()
#     df_melted = pd.melt(df_reset, id_vars=['Date'], var_name=['Price', 'Code'], value_name='Value')
#     df_pivoted = df_melted.pivot_table(index=['Date', 'Code'], columns='Price', values='Value', dropna=False).reset_index()
#     return df_pivoted

# df_data = get_sp_data()

def get_stock_data(code, start, end):
    try:
        data = yf.download(code, start, end)
    except:
        return None
    data = data.drop(data[data.Volume < 10].index)
    if len(data.index) == 0: return None
    business_date = pd.bdate_range(data.index[0], data.index[-1])
    data = pd.DataFrame(data, index=business_date)
    data.index.name = "Date"
    data["Adj Close"] = data["Adj Close"].interpolate(method="linear")
    return data

def stock_download(
    dic,
    start="2001-01-01",
    end="2021-11-30",
    len_data=5000,
    n_stock=50,
    download_dir="data/stocks/",
):
    os.makedirs(download_dir, exist_ok=True)
    count = 0
    stock_dict = {}
    for symbol in dic:
        symbol = symbol if symbol != "BRK.B" else "BRK-B"
        data = get_stock_data(symbol, start, end)
        if data is not None and len(data) > len_data:
            data.to_csv(download_dir + f"{symbol}.csv")
            stock_dict[symbol] = dic[symbol]
            count += 1
            print(symbol)
        else:
            print(f"failed at {symbol}")
        if count >= n_stock:
            break
    return stock_dict

if __name__ == "__main__":
    config = json.load(open("data/data_config.json", "r", encoding="utf8"))
    snp500 = pd.read_csv("data/snp500.csv")
    snp500.loc[snp500.Symbol == "BRK.B", "Symbol"] = "BRK-B"
    snp500 = {tup[2]: tup[1] for tup in snp500.values.tolist()}
    stock_pair = stock_download(
        snp500, len_data=config["LEN_DATA"], n_stock=config["N_STOCK"], download_dir='data/stocks/'
    )
    sp500 = yf.download("^GSPC", config["START"], config["END"])
    sp500.to_csv("data/snp500_index.csv")
    json.dump(stock_pair, open("data/stock.json", "w", encoding="UTF-8"))
 