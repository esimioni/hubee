from device import NumericChangeDevice
from sensor.bme680 import BME680

# @formatter:off
_EP_TEMPERATURE = const(0x04)
_EP_HUMIDITY    = const(0x05)
_EP_PRESSURE    = const(0x06)
_EP_AIR_QUALITY = const(0x07)

_P_SCALE        = 'SC'
# @formatter:on


class EnvironmentDevice(NumericChangeDevice):

    def __init__(self, bme: BME680):
        super().__init__()
        self.bme = bme

    def configure(self, json_conf):
        super().configure(json_conf)
        self.bme.set_refresh_time(self.get_endpoint(), self.min_interval)


class TemperatureSensor(EnvironmentDevice):

    def __init__(self, bme: BME680):
        super().__init__(bme)
        self.celsius = True

    def get_endpoint(self) -> int:
        return _EP_TEMPERATURE

    def read_sensor(self):
        return (self.bme.temperature if self.celsius else self.bme.temperature * 1.8 + 32) + self.offset

    def get_report_value(self):
        return self.str_2_decimals(self.last_reading)

    def configure(self, json_conf: object):
        super().configure(json_conf)
        self.celsius = json_conf[_P_SCALE] is 'C'


class HumiditySensor(EnvironmentDevice):

    def get_endpoint(self) -> int:
        return _EP_HUMIDITY

    def read_sensor(self):
        return self.bme.humidity + self.offset

    def get_report_value(self):
        return self.str_2_decimals(self.last_reading)


class AirQualitySensor(EnvironmentDevice):

    def get_endpoint(self) -> int:
        return _EP_AIR_QUALITY

    def read_sensor(self):
        return (self.bme.gas / 1000) + self.offset  # KOhms

    def get_report_value(self):
        return str(round(self.last_reading))


class PressureSensor(EnvironmentDevice):

    def get_endpoint(self) -> int:
        return _EP_PRESSURE

    def read_sensor(self):
        return self.bme.pressure + self.offset  # hPa

    def get_report_value(self):
        return str(round(self.last_reading))