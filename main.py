from flask import Flask, request, jsonify
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import logging

logging.getLogger().setLevel(logging.INFO)

app = Flask(__name__)


@app.route('/stock/<ticker>', methods=['GET'])
def get_stock_data(ticker):
    period = request.args.get('period', '30d')  # default to 30 days if no period is provided

    # Check if period is 30 days
    if period == '30d':
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        frames = []  # list to hold data frames

        # Loop through each day in the 30 days period
        for i in range(30):
            current_date = start_date + timedelta(days=i)
            next_day = current_date + timedelta(days=1)
            # Convert datetime to string format expected by yfinance
            str_current_date = current_date.strftime('%Y-%m-%d')
            str_next_day = next_day.strftime('%Y-%m-%d')

            # Fetch data for the day
            try:
                data = yf.Ticker(ticker).history(start=str_current_date, end=str_next_day, interval="1h")
                if not data.empty:
                    frames.append(data)
            except IndexError as e:
                logging.error(f"Error fetching data for date {str_current_date} to {str_next_day}: {e}")

        # Combine all the data frames into one
        if frames:
            result = pd.concat(frames)
            result = result.fillna(0).to_dict()
            for key in result.keys():
                result[key] = {str(k): v for k, v in result[key].items()}  # Convert datetime to string

            return jsonify(result)
        else:
            return jsonify({"error": "No data available for the requested period."})

    else:
        return jsonify({"error": "Unsupported period."})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)