import os
from trading_ig import IGService
from trading_ig_config import config
from datetime import datetime, timedelta
# from dotenv import load_dotenv
import numpy as np

# load_dotenv()

# Set up authentication
# config.username = os.getenv('IG_TRADING_USERNAME')
# config.password = os.getenv('IG_TRADING_PASSWORD')
# config.api_key = os.getenv('IG_TRADING_API_KEY')
# config.acc_type = 'demo'  # or 'live' for live trading

# Initialize IG service
try:
    ig_service = IGService(config.username, config.password, config.api_key, config.acc_type)
    ig_service.create_session()
    print("Login Successful")
except Exception as e:
    print(e)

class TradingBot:
    def __init__(self, symbol='CS.D.EURUSD.MINI.IP'):
        self.symbol = symbol
        self.account_info = ig_service.switch_account(config.acc_type, False)
        self.equity = self.account_info['availableToDeal']
        self.risk_limit = 0.05 * self.equity  # Risk not more than 5% of equity

    def fetch_historical_prices(self, interval='MINUTE', num_points=100):
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(minutes=num_points)
            prices = ig_service.fetch_historical_prices(
                epic=self.symbol,
                resolution=interval,
                from_date=start_date.strftime('%Y-%m-%dT%H:%M:%S'),
                to_date=end_date.strftime('%Y-%m-%dT%H:%M:%S')
            )
            return prices['prices']
        except Exception as e:
            print("Error fetching historical prices:", e)
            return []

    def calculate_support_resistance(self, prices):
        try:
            high_prices = [price['highPrice'] for price in prices]
            low_prices = [price['lowPrice'] for price in prices]
            close_prices = [price['closePrice'] for price in prices]

            support_level = min(low_prices)
            resistance_level = max(high_prices)

            return support_level, resistance_level
        except Exception as e:
            print("Error calculating support and resistance levels:", e)
            return None, None

    def calculate_moving_average(self, prices, window=50):
        try:
            close_prices = [price['closePrice'] for price in prices]
            moving_average = np.mean(close_prices[-window:])
            return moving_average
        except Exception as e:
            print("Error calculating moving average:", e)
            return None

    def generate_signal(self):
        try:
            prices = self.fetch_historical_prices()
            if not prices:
                return 'hold'

            current_price = prices[-1]['closePrice']
            support_level, resistance_level = self.calculate_support_resistance(prices)
            moving_average = self.calculate_moving_average(prices)
            if moving_average is None:
                return 'hold'

            if current_price > moving_average and current_price > resistance_level:
                return 'buy'
            elif current_price < moving_average and current_price < support_level:
                return 'sell'
            else:
                return 'hold'
        except Exception as e:
            print("Error generating signal:", e)
            return 'hold'

    def execute_trade(self, side, size=1):
        try:
            if side == 'buy':
                ig_service.create_open_position(
                    epic=self.symbol,
                    direction='BUY',
                    order_type='MARKET',
                    expiry='DFB',
                    size=size,
                    guaranteed_stop=False
                )
                return f"Buy trade executed for {size} units of {self.symbol}"
            elif side == 'sell':
                ig_service.create_open_position(
                    epic=self.symbol,
                    direction='SELL',
                    order_type='MARKET',
                    expiry='DFB',
                    size=size,
                    guaranteed_stop=False
                )
                return f"Sell trade executed for {size} units of {self.symbol}"
            else:
                return "No trade executed."
        except Exception as e:
            print("Error executing trade:", e)
            return "Error executing trade"
        
if __name__ == "__main__":
    trading_bot = TradingBot()
    trading_bot.main()
