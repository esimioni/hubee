import time

import hubee
from device import NumericChangeDevice
from sensor.base import Sensor


class LuxSensor(Sensor):

    def __init__(self):
        self.last_reading_time = None
        self.sample_interval = None
        self.last_reading = None

    # TODO hold first reading after a boot, can be completely off for veml7700
    def check(self):
        if hubee.interval_expired(time.ticks_ms(), self.last_reading_time, self.sample_interval):
            res = self.read_lux()
            if res:
                self.last_reading = res
                self.last_reading_time = time.ticks_ms()

    def setup(self, integration, gain, sample_interval):
        raise NotImplementedError

    def read_lux(self):
        raise NotImplementedError

    # def is_initialized(self):
    #     raise NotImplementedError

    def get_last_reading(self):
        return self.last_reading


class LuxDevice(NumericChangeDevice):

    def __init__(self, sensor: LuxSensor):
        super().__init__()
        self.sensor = sensor
        # while not self.sensor.is_initialized():
        #     self.sensor.check()
        #     time.sleep_ms(105)

    def get_endpoint(self) -> int:
        return 0x08  #_EP_LUX

    def read_sensor(self):
        return self.sensor.get_last_reading()

    def get_report_value(self):
        return self._str_2_decimals(self.last_reading)

    def configure(self, json_conf):
        super().configure(json_conf)
        self.sensor.setup(json_conf['IT'], json_conf['GA'], self.min_interval)