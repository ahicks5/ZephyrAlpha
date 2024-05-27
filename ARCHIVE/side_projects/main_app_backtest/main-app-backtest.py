from flask import Flask, render_template, request
from side_projects.backtest import print_gain_or_loss  # Ensure this function returns results
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Choose a secret key
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/backtest', methods=['GET', 'POST'])
def backtest():
    if request.method == 'POST':
        stock_ticker = request.form.get('stockTicker')
        date_of_event = request.form.get('dateOfEvent')
        analysis_results = print_gain_or_loss(stock_ticker, date_of_event)
        return render_template('backtest_results.html',
                               stock_ticker=analysis_results['stock_ticker'],
                               target_date=analysis_results['target_date'],
                               results=analysis_results['results'])
    else:
        return render_template('backtest.html')

@app.route('/chat')
def chat():
    return render_template('game_page.html')

@socketio.on('message')
def handleMessage(msg):
    print('Message: ' + msg)
    send(msg, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)  # Only for development

