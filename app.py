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

# print(account)
# ig.getAvailable()
class TradingBot:
    def __init__(self, symbol='IX.D.FTSE.IFM.IP'):
        self.symbol = symbol
        # self.account_info = ig_service.switch_account(config.acc_type, config.acc_id)
        # self.equity = self.account_info['availableToDeal']
        self.equity = account.loc['XQWAV', 'balance']['balance']
        self.risk_limit = 0.05 * self.equity  # Risk not more than 5% of equity

    def fetch_historical_prices(self, interval='DAY'):
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(weeks=4)
            prices = ig_service.getPrices(
                epic=self.symbol,
                resolution=interval,
                start=str(start_date),
                end=str(end_date)
            )
            return prices
        except Exception as e:
            print("Error fetching historical prices:", e)
            return []

    def calculate_support_resistance(self, prices):
        try:
            bid_prices = [entry['bid'] for entry in prices['closePrice'].tolist()]
            ask_prices = [entry['ask'] for entry in prices['closePrice'].tolist()]
            high = max(max(bid_prices), max(ask_prices))
            low = min(min(bid_prices), min(ask_prices))

            # Support level is the lowest closing price
            support = low

            # Resistance level is the highest closing price
            resistance = high

            return support, resistance
        except Exception as e:
            print("Error calculating support and resistance levels:", e)
            return None, None

    def calculate_moving_average(self, prices, window=4):
        try:
            bid_prices = [entry['bid'] for entry in prices['closePrice'].tolist()]
            ask_prices = [entry['ask'] for entry in prices['closePrice'].tolist()]
            
            close_prices = np.array([(bid + ask) / 2 for bid, ask in zip(bid_prices, ask_prices)])
            # Calculate the simple moving average (SMA) using Ta-Lib
            moving_average = talib.SMA(close_prices, timeperiod=window)[-1]
            return moving_average
        except Exception as e:
            print("Error calculating moving average:", e)
            return None

    def calculate_pivot_point(self,prices):
        """
        Calculate the pivot point.

        Args:
        data (dict): Dictionary containing bid, ask, and last traded prices.

        Returns:
        float: The pivot point.
        """
        high = max([entry['ask'] for entry in prices['closePrice'].tolist()])
        low =  min([entry['bid'] for entry in prices['closePrice'].tolist()])
        close = max([entry['lastTraded'] if entry['lastTraded'] is not None else (entry['bid'] + entry['ask']) / 2 for entry in prices['closePrice'].tolist()])
        pivot_point = (high + low + close) / 3
        return pivot_point

    def generate_signal(self):
        try:
            prices = self.fetch_historical_prices()
            if prices is None or prices.empty:
                print("hold")
                return 'hold'
            # else:
            #     return prices

            current_price = prices.iloc[-1]['closePrice']['bid']
            support_level, resistance_level = self.calculate_support_resistance(prices)
            moving_average = self.calculate_moving_average(prices)
            pivot_point = self.calculate_pivot_point(prices)

            if moving_average is None or pivot_point is None:
                print("hold")
                return 'hold'
            # else:
                # return moving_average, pivot_point
            # return current_price, moving_average, support_level, resistance_level, pivot_point
            # Generating the signal based on conditions
            if current_price > moving_average and current_price > resistance_level and current_price > pivot_point:
                print("buy")
                return 'buy'
            elif current_price < moving_average and current_price < support_level and current_price < pivot_point:
                print("sell")
                return 'sell'
            else:
                print("hold")
                return 'hold'
        except Exception as e:
            print("Error generating signal:", e)
        #     return 'hold'


    def execute_trade(self, size=1):
        try:
            side = 'buy'
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
                    guaranteedStop=False
                )
                print(f"Buy trade executed for {size} units of {self.symbol}")
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
                    guaranteedStop=False
                )
                print(f"Sell trade executed for {size} units of {self.symbol}")
                return f"Sell trade executed for {size} units of {self.symbol}"
            else:
                print("No trade executed.")
                return("No trade executed.")
        except Exception as e:
            print("Error executing trade:", e)
            return "Error executing trade"

def main():
    trading_bot = TradingBot()
    prices = trading_bot.fetch_historical_prices()
    # trading_bot.calculate_support_resistance(prices)
    # trading_bot.calculate_moving_average(prices)
    # trading_bot.calculate_pivot_point(prices)
    # trading_bot.generate_signal()
    trading_bot.execute_trade()

if __name__ == "__main__":
    main()
    # You can call methods of trading_bot here as needed.
