import yfinance as yf
from datetime import datetime
from FOC import FOC, OptionType
import pandas as pd
import pytz
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import HTML
import numpy as np

ref_FOC = FOC()


def get_earnings_date(ticker):
    current_date = datetime.now(pytz.timezone('US/Eastern')).date()

    stock = yf.Ticker(ticker)
    earnings_dates = stock.get_earnings_dates()

    next_earnings_dates = earnings_dates[earnings_dates.index.date > current_date]

    next_earnings_date = next_earnings_dates.index.min()

    return next_earnings_date.replace(tzinfo=pytz.timezone('US/Eastern'))


def fetch_earnings_date_and_days(ticker):
    stock = yf.Ticker(ticker)
    current_price = stock.history(period="1d")['Close'].iloc[-1]  # Fetch current stock price
    earnings_date = get_earnings_date(ticker)

    if earnings_date:
        days_until = (earnings_date - datetime.now(pytz.timezone('US/Eastern'))).days
        earnings_date_str = earnings_date.strftime('%Y-%m-%d %H:%M:%S %Z%z')
    else:
        days_until = "N/A"
        earnings_date_str = "Earnings date not found"

    expiration_dates = ref_FOC.get_expiration_dates(ticker)
    expiration_dates_dt = pd.to_datetime(expiration_dates)
    expiration_date = expiration_dates_dt[0]

    options_chain_df = ref_FOC.get_options_chain(ticker, expiration_date.strftime('%Y-%m-%d'), OptionType.CALLPUT)
    atm_call_ask, atm_put_ask, atm_call_strike, atm_put_strike = find_atm_options(options_chain_df)
    straddle_cost = atm_call_ask + atm_put_ask
    expected_move_percentage = (straddle_cost / current_price) * 100

    return {
        "Next Earnings Date": earnings_date_str,
        "Days Until Earnings": days_until,
        "Current Price": current_price,
        "ATM Call Strike": atm_call_strike,
        "ATM Call Ask": atm_call_ask,
        "ATM Put Strike": atm_put_strike,
        "ATM Put Ask": atm_put_ask,
        "Expected Move (%)": expected_move_percentage
    }, options_chain_df


def find_atm_options(options_chain_df):
    atm_call_strike = options_chain_df[options_chain_df['c_colour'] == True]['strike'].max()
    atm_put_strike = options_chain_df[options_chain_df['p_colour'] == True]['strike'].min()

    atm_call_option = options_chain_df[
        (options_chain_df['strike'] == atm_call_strike) & (options_chain_df['c_colour'] == True)]
    atm_put_option = options_chain_df[
        (options_chain_df['strike'] == atm_put_strike) & (options_chain_df['p_colour'] == True)]

    atm_call_ask = atm_call_option['c_Ask'].mean()
    atm_put_ask = atm_put_option['p_Ask'].mean()

    return atm_call_ask, atm_put_ask, atm_call_strike, atm_put_strike


def main():
    ticker = input("Enter the ticker symbol: ")
    print(f"Fetching data for {ticker}...\n")

    data, options_chain_df = fetch_earnings_date_and_days(ticker)

    html_table = pd.DataFrame(data, index=[0]).to_html(index=False)
    print(html_table)

    image_path = generate_strangle_graph(data["Current Price"], ticker, data["ATM Call Ask"], data["ATM Put Ask"])
    data["Graph"] = f'<a href="{image_path}" target="_blank"><img src="{image_path}" width="400"></a>'

    html_table_with_graph = pd.DataFrame(data, index=[0]).to_html(index=False, escape=False)
    print(html_table_with_graph)


import numpy as np
import matplotlib.pyplot as plt

def generate_strangle_graph(current_price, ticker, atm_call_ask, atm_put_ask):
    plt.figure(figsize=(10, 6))

    # Plot the current stock price as a vertical line
    plt.axvline(x=current_price, color='blue', linewidth=2, label='Current Stock Price')

    # Calculate the end points for the call and put spans
    call_span_end = current_price + atm_call_ask
    put_span_start = current_price - atm_put_ask

    # Highlight the span for the ATM call ask
    plt.axvspan(current_price, call_span_end, color='green', alpha=0.3, label='ATM Call Ask Span')
    # Highlight the span for the ATM put ask
    plt.axvspan(put_span_start, current_price, color='red', alpha=0.3, label='ATM Put Ask Span')

    # Set the x-axis to span 50 units below and 50 units above the current stock price
    plt.xlim(current_price - 50, current_price + 50)

    # Annotate the plot with the end points of the call and put spans
    plt.text(call_span_end, 0, f'{call_span_end:.2f}', horizontalalignment='center', verticalalignment='bottom', color='green')
    plt.text(put_span_start, 0, f'{put_span_start:.2f}', horizontalalignment='center', verticalalignment='bottom', color='red')

    plt.xlabel('Stock Price')
    plt.ylabel('Option Ask Price Impact')
    plt.title(f'Straddle Value Composition for {ticker}')
    plt.legend()
    plt.tight_layout()

    # Save the plot as an image file
    image_path = f"{ticker}_straddle_value_composition.png"
    plt.savefig(image_path)

    # Close the plot figure to avoid displaying it in non-graphical environments
    plt.close()

    return image_path

if __name__ == "__main__":
    main()
