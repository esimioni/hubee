import time

from sensor.presence import PresenceDevice


# TOF10120 Laser distance sensor
class ProximitySensor(PresenceDevice):

    def __init__(self, i2c):
        super().__init__()
        self.i2c = i2c
        self.addr = 0x52
        self.min_trigger_distance = 0
        self.max_trigger_distance = 0

    def get_endpoint(self) -> int:
        return 0x09  #_EP_PROXIMITY

    def is_present(self):
        self.i2c.writeto(self.addr, b'0x00')
        time.sleep_ms(3)  # TODO: Can this sleep be removed? Maybe check in 2 steps
        data = self.i2c.readfrom(self.addr, 2)
        data = int.from_bytes(data, 'big')
        return self.min_trigger_distance <= data <= self.max_trigger_distance

    def configure(self, json_conf):
        super().configure(json_conf)
        self.min_trigger_distance = json_conf['MI']
        self.max_trigger_distance = json_conf['MA']