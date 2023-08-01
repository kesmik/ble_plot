from config import Config

class RSSIConv:
    settings = Config().get_settings()
    N = settings['rssi_conv']['N_VAL']
    measured_pwr = settings['rssi_conv']['MEASURED_PWR']

    @classmethod
    def get_dist(cls, rssi):
        return pow(10, ((cls.measured_pwr-rssi)/(10*cls.N)))
