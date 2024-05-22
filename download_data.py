import os
import json
import yfinance as yf
import pandas as pd
import random


def get_stock_data(code, start, end, min_volumn=10):
    try:
        data = yf.download(code, start, end)
    except:
        print(f"failed at downloading {code}")
        return None
    data = data.drop(data[data.Volume < min_volumn].index)
    if len(data.index) == 0: return None
    business_date = pd.bdate_range(data.index[0], data.index[-1])
    data = pd.DataFrame(data, index=business_date)
    data.index.name = "Date"
    return data

def stock_download(
    symbols,
    start="2001-01-01",
    end="2021-11-30",
    len_data=5000,
    n_stock=50,
    download_dir="data/stocks/",
):
    os.makedirs(download_dir, exist_ok=True)
    count = 0
    stock_dict = {}
    for symbol in symbols:
        symbol = symbol if symbol != "BRK.B" else "BRK-B"
        data = get_stock_data(symbol, start, end)
        if data is not None and len(data) > len_data:
            data.to_csv(download_dir + f"{symbol}.csv")
            stock_dict[symbol] = symbol
            count += 1
            print(symbol)
        else:
            print(f"failed at {symbol}")
        if count >= n_stock:
            break
    return stock_dict

def get_return_df(stock_dic, in_path="data/stocks/", out_path="data/"):
    for i, ticker in enumerate(stock_dic):
        stock = in_path + f"{ticker}.csv"
        stock_df = pd.read_csv(stock, index_col="Date")[["Adj Close"]]
        if i == 0:
            return_df = stock_df
            return_df.columns = [ticker]
        else:
            return_df[ticker] = stock_df
    return_df = return_df.dropna()
    return_df.to_csv(out_path + "return_df.csv")
    return return_df

if __name__ == "__main__":
    config = json.load(open("data/data_config.json", "r", encoding="utf8"))
    snp500 = pd.read_csv("data/snp500.csv")
    snp500.loc[snp500.Symbol == "BRK.B", "Symbol"] = "BRK-B"
    snp500 = [tup[2] for tup in snp500.values.tolist()]
    random.shuffle(snp500)

    stock_pair = stock_download(
        snp500, start=config["START"], end=config["END"], 
        len_data=config["LEN_DATA"], n_stock=config["N_STOCK"], download_dir='data/stocks/'
    )
    sp500 = yf.download("^GSPC", config["START"], config["END"])
    return_df = get_return_df(stock_pair)
    sp500.to_csv("data/snp500_index.csv")
    json.dump(stock_pair, open("data/stock.json", "w", encoding="UTF-8"))
 
