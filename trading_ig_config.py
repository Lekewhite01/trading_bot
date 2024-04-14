from dotenv import load_dotenv
import os

load_dotenv()

class Config(object):
    """
    Configuration class to hold credentials and settings for IG Trading.
    """
    def __init__(self):
        self.username = os.getenv('IG_SERVICE_USERNAME')
        self.password = os.getenv('IG_SERVICE_PASSWORD')
        self.api_key = os.getenv('IG_SERVICE_API_KEY')
        self.acc_type = os.getenv('IG_SERVICE_ACC_TYPE')  # Could be "LIVE" or "DEMO"
        # self.acc_number = "ABC123"  # Uncomment and set appropriately if needed

config = Config()