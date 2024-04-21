import os
from trading_ig import IGService
from trading_ig_config import config
from datetime import datetime, timedelta
import numpy as np
import talib
import igapi

# Set up authentication
# config.username = os.getenv('IG_TRADING_USERNAME')
# config.password = os.getenv('IG_TRADING_PASSWORD')
# config.api_key = os.getenv('IG_TRADING_API_KEY')
# config.acc_type = 'demo'  # or 'live' for live trading

# Initialize IG service
try:
    # ig_service = IGService(config.username, config.password, config.api_key, config.acc_type,
    #                        config.acc_id)
    # ig_service.create_session(version='3')
    ig_service = igapi.IG(config.api_key, config.username, config.password, config.acc_id, config.acc_type)
    print(ig_service.getVersion())
    ig_service.login()
    print("Login Successful")
except Exception as e:
    print(e)

account = ig_service.account()

print(account)
# ig.getAvailable()
class TradingBot:
    def __init__(self, symbol='CS.D.EURUSD.MINI.IP'):
        self.symbol = symbol
        # self.account_info = ig_service.switch_account(config.acc_type, config.acc_id)
        # self.equity = self.account_info['availableToDeal']
        self.equity = account.loc['XQWAV', 'balance']['balance']
        self.risk_limit = 0.05 * self.equity  # Risk not more than 5% of equity

    # def initialize_account_info(self, default_account):
    #     try:
    #         return ig_service.switch_account(default_account)
    #     except Exception as e:
    #         print("Error initializing account info:", e)
    #         return None

    def fetch_historical_prices(self, interval='MINUTE', num_points=100):
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(minutes=num_points)
            prices = ig_service.getPrices(
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
            high_prices = np.array([price['highPrice'] for price in prices])
            low_prices = np.array([price['lowPrice'] for price in prices])
            close_prices = np.array([price['closePrice'] for price in prices])

            support_level = np.min(low_prices)
            resistance_level = np.max(high_prices)

            return support_level, resistance_level
        except Exception as e:
            print("Error calculating support and resistance levels:", e)
            return None, None

    def calculate_moving_average(self, prices, window=50):
        try:
            close_prices = np.array([price['closePrice'] for price in prices])
            moving_average = talib.SMA(close_prices, timeperiod=window)[-1]
            return moving_average
        except Exception as e:
            print("Error calculating moving average:", e)
            return None

    def calculate_pivot_point(self, prices):
        try:
            high_prices = np.array([price['highPrice'] for price in prices])
            low_prices = np.array([price['lowPrice'] for price in prices])
            close_prices = np.array([price['closePrice'] for price in prices])

            pivot_point = talib.PIVOT(close_prices, high_prices, low_prices, close_prices)[-1]
            return pivot_point
        except Exception as e:
            print("Error calculating pivot point:", e)
            return None

    def generate_signal(self):
        try:
            prices = self.fetch_historical_prices()
            if not prices:
                return 'hold'

            current_price = prices[-1]['closePrice']
            support_level, resistance_level = self.calculate_support_resistance(prices)
            moving_average = self.calculate_moving_average(prices)
            pivot_point = self.calculate_pivot_point(prices)
            if moving_average is None or pivot_point is None:
                return 'hold'

            if current_price > moving_average and current_price > resistance_level and current_price > pivot_point:
                return 'buy'
            elif current_price < moving_average and current_price < support_level and current_price < pivot_point:
                return 'sell'
            else:
                return 'hold'
        except Exception as e:
            print("Error generating signal:", e)
            return 'hold'

    def execute_trade(self, side, size=1):
        try:
            if side == 'buy':
                ig_service.createPosition(
                    currency = 'GBP',
                    epic=self.symbol,
                    direction='BUY',
                    orderType='MARKET',
                    expiry='-',
                    size=size,
                    forceOpen=True,
                    limitDistance=None,
                    stopDistance=None,
                    guaranteed_stop=False
                )
                return f"Buy trade executed for {size} units of {self.symbol}"
            elif side == 'sell':
                ig_service.createPosition(
                    currency = 'GBP',
                    epic=self.symbol,
                    direction='SELL',
                    orderType='MARKET',
                    expiry='-',
                    size=size,
                    forceOpen=True,
                    limitDistance=None,
                    stopDistance=None,
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
    # You can call methods of trading_bot here as needed.
