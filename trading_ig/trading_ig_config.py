import os
from dotenv import load_dotenv

load_dotenv()


class config(object):
    username = os.getenv("IG_USERNAME")
    password = os.getenv("IG_PASSWORD")
    api_key = os.getenv("IG_API_KEY")
    acc_type = os.getenv("IG_ACC_TYPE")  # LIVE / DEMO
    acc_number = os.getenv("IG_ACC_NUMBER")
