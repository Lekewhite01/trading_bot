from dotenv import load_dotenv
import os

load_dotenv()

class config(object):
    username = os.getenv('IG_TRADING_USERNAME')
    password = os.getenv('IG_TRADING_PASSWORD')
    api_key = os.getenv('IG_TRADING_API_KEY')
    acc_type = "DEMO"  # LIVE / DEMO
    # acc_number = "ABC123"