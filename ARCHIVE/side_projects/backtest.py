import yfinance as yf
from datetime import datetime, timedelta


def get_last_trading_day():
    today = datetime.today().date()
    while today.weekday() > 4:  # If it's Saturday or Sunday, subtract a day
        today -= timedelta(days=1)
    return today


def get_sp500_return(start_date, end_date, investment=1000):
    sp500 = yf.Ticker("^GSPC")
    sp500_data = sp500.history(start=start_date, end=end_date)
    if not sp500_data.empty:
        initial_price = sp500_data.iloc[0]['Close']
        final_price = sp500_data.iloc[-1]['Close']
        return ((final_price - initial_price) / initial_price) * investment
    return 0


def print_gain_or_loss(stock_ticker, target_date):
    target_date_dt = datetime.strptime(target_date, '%Y-%m-%d').date()
    last_trading_day = get_last_trading_day()

    stock_data = yf.download(stock_ticker, start=target_date_dt - timedelta(days=1),
                             end=last_trading_day + timedelta(days=1))
    stock_data.index = stock_data.index.date  # Convert index to date-only format

    if target_date_dt not in stock_data.index:
        print(f"Data for {target_date} not available.")
        return

    target_date_close = stock_data.loc[target_date_dt, 'Adj Close']
    prior_date_close = stock_data.loc[target_date_dt - timedelta(days=1), 'Adj Close']

    if target_date_close > prior_date_close:
        print("The analysis could not be completed as there was a gain from the previous day.")
    else:
        result = analyze_recovery(stock_data, target_date, prior_date_close, target_date_close, stock_ticker)
        return result


def analyze_recovery(stock_data, target_date_str, day_0_price, day_1_price, stock_ticker):
    target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
    loss_amount = day_0_price - day_1_price
    investment = 1000
    recovery_thresholds = [25, 50, 75, 100]
    recovery_results = []

    filtered_data = stock_data.loc[target_date + timedelta(days=1):]

    for percent in recovery_thresholds:
        target_price = day_1_price + (loss_amount * (percent / 100))
        condition = filtered_data['Adj Close'] >= target_price
        if condition.any():
            recovery_day = condition.idxmax()
            days_to_recovery = (recovery_day - target_date).days
            stock_gain = ((filtered_data.at[recovery_day, 'Adj Close'] / day_1_price) - 1) * 100
            absolute_stock_gain = ((filtered_data.at[recovery_day, 'Adj Close'] - day_1_price) / day_1_price) * investment
            sp500_return = get_sp500_return(target_date, recovery_day)
            sp500_gain = (sp500_return / investment) * 100
            alpha = stock_gain - sp500_gain

            recovery_results.append({
                'recovery_percentage': percent,
                'days': days_to_recovery,
                'stock_gain': stock_gain,
                'absolute_gain': absolute_stock_gain,
                'sp500_return': sp500_return,
                'alpha': alpha,
            })
        else:
            recovery_results.append({
                'recovery_percentage': percent,
                'days': 'N/A',
                'stock_gain': 'N/A',
                'absolute_gain': 'N/A',
                'sp500_return': 'N/A',
                'alpha': 'N/A',
            })

    return {
        'stock_ticker': stock_ticker,
        'target_date': target_date_str,
        'results': recovery_results  # This is the list of dictionaries with the recovery analysis
    }


print_gain_or_loss('AAPL', '2022-11-03')