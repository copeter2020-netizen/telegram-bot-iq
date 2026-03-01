import time
from iqoptionapi.stable_api import IQ_Option

class IQConnector:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.api = IQ_Option(email, password)

    def connect(self):
        check, reason = self.api.connect()
        if check:
            self.api.change_balance("PRACTICE")
            return True
        else:
            print("Error conectando:", reason)
            return False

    def get_candles(self, pair="EURUSD-OTC", timeframe=60, count=100):
        end_from_time = time.time()
        candles = self.api.get_candles(pair, timeframe, count, end_from_time)
        return candles
