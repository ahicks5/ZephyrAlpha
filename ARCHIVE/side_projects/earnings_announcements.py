import yfinance as yf
from datetime import datetime
from FOC import FOC, OptionType
import pandas as pd
import matplotlib.pyplot as plt
import pytz

ref_FOC = FOC()


def get_earnings_date(ticker):
    current_date = datetime.now(pytz.timezone('US/Eastern')).date()

    stock = yf.Ticker(ticker)
    earnings_dates = stock.get_earnings_dates()

    next_earnings_dates = earnings_dates[earnings_dates.index.date > current_date]

    next_earnings_date = next_earnings_dates.index.min()

    return next_earnings_date.replace(tzinfo=pytz.timezone('US/Eastern'))

def fetch_earnings_date_and_days(ticker):
    earnings_date = get_earnings_date(ticker)

    if earnings_date:
        days_until = (earnings_date - datetime.now(pytz.timezone('US/Eastern'))).days
        print(f"Earnings Date for {ticker}: {earnings_date.strftime('%Y-%m-%d %H:%M:%S %Z%z')}, Days Until Earnings: {days_until}")
    else:
        print("Earnings date not found")

    expiration_dates = ref_FOC.get_expiration_dates(ticker)
    expiration_dates_dt = pd.to_datetime(expiration_dates)
    expiration_date = expiration_dates_dt[0]

    options_chain_df = ref_FOC.get_options_chain(ticker, expiration_date.strftime('%Y-%m-%d'), OptionType.CALLPUT)
    options_chain_df['strangle_price'] = options_chain_df['c_Ask'] + options_chain_df['p_Ask']
    options_chain_df['c_percentage'] = (options_chain_df['c_Ask'] / options_chain_df['strangle_price']) * 100
    options_chain_df['p_percentage'] = (options_chain_df['p_Ask'] / options_chain_df['strangle_price']) * 100

    filtered_options_chain_df = options_chain_df[(options_chain_df['c_percentage'] >= 1) & (options_chain_df['p_percentage'] >= 1)]
    grouped_strangles = filtered_options_chain_df.groupby('strike').agg({
        'strangle_price': 'mean',
        'c_percentage': 'mean',
        'p_percentage': 'mean'
    }).reset_index()

    for index, row in grouped_strangles.iterrows():
        print(f"Strike: {row['strike']}, Average Strangle Price: {row['strangle_price']:.2f}, " +
              f"Call Contribution: {row['c_percentage']:.2f}%, Put Contribution: {row['p_percentage']:.2f}%")

    return grouped_strangles, options_chain_df



def plot_strangle_prices(grouped_strangles, ticker):
    plt.figure(figsize=(12, 7))
    plt.style.use('seaborn-darkgrid')
    grouped_strangles['c_contribution'] = (grouped_strangles['strangle_price'] * grouped_strangles['c_percentage']) / 100
    grouped_strangles['p_contribution'] = (grouped_strangles['strangle_price'] * grouped_strangles['p_percentage']) / 100

    for index, row in grouped_strangles.iterrows():
        if row['p_contribution'] > 0:
            plt.bar(row['strike'], row['p_contribution'], color='red', label='Put Contribution' if index == 0 else "", width=2)
        if row['c_contribution'] > 0:
            plt.bar(row['strike'], row['c_contribution'], bottom=row['p_contribution'] if row['p_contribution'] > 0 else 0, color='green', label='Call Contribution' if index == 0 else "", width=2)

    plt.xticks(grouped_strangles['strike'], rotation=90)
    plt.gcf().subplots_adjust(bottom=0.2)
    plt.xlabel('Strike Price')
    plt.ylabel('Price / Contribution')
    plt.title(f'Strangle Prices and Contributions for {ticker}')
    plt.legend()
    plt.show()

def find_atm_options(options_chain_df):
    atm_call_strike = options_chain_df[options_chain_df['c_colour'] == True]['strike'].max()
    atm_put_strike = options_chain_df[options_chain_df['p_colour'] == True]['strike'].min()

    atm_call_option = options_chain_df[(options_chain_df['strike'] == atm_call_strike) & (options_chain_df['c_colour'] == True)]
    atm_put_option = options_chain_df[(options_chain_df['strike'] == atm_put_strike) & (options_chain_df['p_colour'] == True)]

    atm_call_ask = atm_call_option['c_Ask'].mean()
    atm_put_ask = atm_put_option['p_Ask'].mean()

    return atm_call_ask, atm_put_ask, atm_call_strike, atm_put_strike

def estimate_move_from_straddle(options_chain_df, stock_price):
    atm_call_ask, atm_put_ask, atm_call_strike, atm_put_strike = find_atm_options(options_chain_df)
    straddle_cost = atm_call_ask + atm_put_ask  # Corrected to use asks found by find_atm_options
    expected_move_percentage = (straddle_cost / stock_price) * 100

    print(f"Estimated move based on ATM straddle: {expected_move_percentage:.2f}%")
    return expected_move_percentage

def main():
    ticker = input("Enter the ticker symbol: ")
    print(f"Fetching data for {ticker}...\n")
    grouped_strangles, options_chain_df = fetch_earnings_date_and_days(ticker)

    stock = yf.Ticker(ticker)
    get_earnings_date(ticker)
    current_price = stock.history(period="1d")['Close'].iloc[-1]  # Fetch current stock price

    expected_move_percentage = estimate_move_from_straddle(options_chain_df, current_price)
    print(f"Expected move based on ATM straddle: {expected_move_percentage:.2f}%")

    plot_strangle_prices(grouped_strangles, ticker)  # Uncomment if you wish to plot

if __name__ == "__main__":
    main()
