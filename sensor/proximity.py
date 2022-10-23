import time

import hubee
from sensor.presence import PresenceDevice


# TOF10120 Laser distance sensor
class ProximitySensor(PresenceDevice):

    def __init__(self, i2c):
        super().__init__()
        self.i2c = i2c
        self.addr = 0x52
        self.trigger_distance = 0x00

    def get_endpoint(self) -> int:
        return hubee.EP_PROXIMITY

    def is_present(self):
        self.i2c.writeto(self.addr, b'0x00')
        time.sleep_ms(0x03)  # TODO: Can this sleep be removed? Maybe check in 2 steps
        data = self.i2c.readfrom(self.addr, 2)
        data = int.from_bytes(data, 'big')
        return data <= self.trigger_distance

    def configure(self, json_conf: object):
        super().configure(json_conf)
        self.trigger_distance = json_conf[hubee.P_DISTANCE]