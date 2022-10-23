import hubee
from device import NumericChangeDevice
from sensor.bme680 import BME680


class EnvironmentDevice(NumericChangeDevice):

    def __init__(self, bme: BME680):
        super().__init__()
        self.bme = bme


class TemperatureSensor(EnvironmentDevice):

    def __init__(self, bme: BME680):
        super().__init__(bme)
        self.celsius = True

    def get_endpoint(self) -> int:
        return hubee.EP_TEMPERATURE

    def read_sensor(self):
        return (self.bme.temperature if self.celsius else self.bme.temperature * 1.8 + 32) + self.offset

    def get_report_value(self):
        return hubee.str_2_decimals(self.last_reading)

    def configure(self, json_conf: object):
        super().configure(json_conf)
        self.celsius = json_conf[hubee.P_SCALE] is 'C'


class HumiditySensor(EnvironmentDevice):

    def get_endpoint(self) -> int:
        return hubee.EP_HUMIDITY

    def read_sensor(self):
        return self.bme.humidity + self.offset

    def get_report_value(self):
        return hubee.str_2_decimals(self.last_reading)


class AirQualitySensor(EnvironmentDevice):

    def get_endpoint(self) -> int:
        return hubee.EP_AIR_QUALITY

    def read_sensor(self):
        return (self.bme.gas / 1000) + self.offset  # KOhms

    def get_report_value(self):
        return str(round(self.last_reading))


class PressureSensor(EnvironmentDevice):

    def get_endpoint(self) -> int:
        return hubee.EP_PRESSURE

    def read_sensor(self):
        return self.bme.pressure + self.offset  # hPa

    def get_report_value(self):
        return str(round(self.last_reading))