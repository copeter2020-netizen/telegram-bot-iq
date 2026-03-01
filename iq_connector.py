import time
from iqoptionapi.stable_api import IQ_Option


class ConectorIQ:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.api = IQ_Option(email, password)

    def conectar(self):
        check, reason = self.api.connect()
        if check:
            self.api.change_balance("PRACTICE")
            return True
        else:
            print("Error conectando:", reason)
            return False

    def obtener_velas(self, par="EURUSD-OTC", periodo=60, cantidad=120):
        fin = time.time()
        velas = self.api.get_candles(par, periodo, cantidad, fin)
        return velas
