import time

from device import NumericChangeDevice
from sensor.base import Sensor

# @formatter:off
_CMD_BIT       = const(0xA0)
_ENABLE_PWRON  = const(0x01)
_ENABLE_PWROFF = const(0x00)
_ENABLE_AEN    = const(0x02)
_ENABLE_AIEN   = const(0x10)
_LUX_DF        = 408.0
_LUX_COEFB     = 1.64
_LUX_COEFC     = 0.59
_LUX_COEFD     = 0.86

_GAIN_LOW      = const(0x00)
_GAIN_MED      = const(0x10)
_GAIN_HIGH     = const(0x20)
_GAIN_MAX      = const(0x30)

_SENSOR_ADDR   = const(0x29)

_REG_ENABLE    = const(0x00)
_REG_CTRL      = const(0x01)
_REG_CHAN0_LOW = const(0x14)
_REG_CHAN1_LOW = const(0x16)
_INTTIME_100MS = const(0x00)
_INTTIME_200MS = const(0x01)
_INTTIME_300MS = const(0x02)
_INTTIME_400MS = const(0x03)
_INTTIME_500MS = const(0x04)
_INTTIME_600MS = const(0x05)

_CASE_INTEG = {
    _INTTIME_100MS: 100.,
    _INTTIME_200MS: 200.,
    _INTTIME_300MS: 300.,
    _INTTIME_400MS: 400.,
    _INTTIME_500MS: 500.,
    _INTTIME_600MS: 600.,
}

_CASE_GAIN = {
    _GAIN_LOW : 1.,
    _GAIN_MED : 25.,
    _GAIN_HIGH: 428.,
    _GAIN_MAX : 9876.,
}

_EP_LUX = const(0x08)
# @formatter:on


class SMBusEmulator:

    def __init__(self, i2c):
        self.i2c = i2c

    def _bytes_to_int(self, data):
        return data[0] + (data[1] << 0x08)

    def write_byte_data(self, addr, cmd, val):
        buf = bytes([cmd, val])
        self.i2c.writeto(addr, buf)

    def read_word_data(self, addr, cmd):
        assert cmd < 256
        buf = bytes([cmd])
        self.i2c.writeto(addr, buf)
        data = self.i2c.readfrom(addr, 0x04)
        return self._bytes_to_int(data)


# Normally it would sleep for 1 second to perform a reading. Changed it not to sleep for regular readings,
# so it  can be used in a loop with other devices without impacting their responsiveness.
class Tsl2591(Sensor):

    def __init__(self, i2c, integration = _INTTIME_100MS, gain = _GAIN_HIGH, sample_interval = 1000):
        self._bus = SMBusEmulator(i2c)
        self._integ_time = integration
        self._gain = gain
        self._last_reading_time = 0x00
        self._last_reading = 0x00
        self._enabled_wait_ms = int((0.120 * self._integ_time + 0x01) * 1000)
        self.set_sample_interval(sample_interval)
        self._setup()

    def set_sample_interval(self, sample_interval):
        self._sample_interval = sample_interval

    def _setup(self):
        self._enable()
        self._bus.write_byte_data(
            _SENSOR_ADDR,
            _CMD_BIT | _REG_CTRL,
            self._integ_time | self._gain
        )
        self._disable()

    def _calculate_lux(self, full, ir):
        if full == 0xFFFF | ir == 0xFFFF:
            return 0x00

        atime = _CASE_INTEG[self._integ_time]
        again = _CASE_GAIN[self._gain]

        cpl = atime * again / _LUX_DF
        lux1 = (full - (_LUX_COEFB * ir)) / cpl
        lux2 = ((_LUX_COEFC * full) - (_LUX_COEFD * ir)) / cpl
        return max([lux1, lux2])

    def _enable(self):
        self._bus.write_byte_data(_SENSOR_ADDR, _CMD_BIT | _REG_ENABLE, _ENABLE_PWRON | _ENABLE_AEN | _ENABLE_AIEN)
        self._enabled_time = time.ticks_ms()

    def _disable(self):
        self._bus.write_byte_data(_SENSOR_ADDR, _CMD_BIT | _REG_ENABLE, _ENABLE_PWROFF)
        self._enabled_time = 0x00

    def _get_full_luminosity(self):
        if self._enabled_time == 0x00:
            self._enable()
            return

        if time.ticks_ms() - self._enabled_time >= self._enabled_wait_ms:
            full = self._bus.read_word_data(_SENSOR_ADDR, _CMD_BIT | _REG_CHAN0_LOW)
            ir = self._bus.read_word_data(_SENSOR_ADDR, _CMD_BIT | _REG_CHAN1_LOW)
            self._disable()
            return full, ir

    def check(self):
        if not time.ticks_ms() - self._last_reading_time < self._sample_interval:
            res = self._get_full_luminosity()
            if res:
                self._last_reading = self._calculate_lux(res[0], res[1])
                self._last_reading_time = time.ticks_ms()

    def get_last_reading(self):
        return self._last_reading

    def is_initialized(self):
        return self._last_reading_time > 0


class LuxSensor(NumericChangeDevice):

    def __init__(self, tsl: Tsl2591):
        super().__init__()
        self.tsl = tsl
        while not self.tsl.is_initialized():
            self.tsl.check()
            time.sleep_ms(105)

    def get_endpoint(self) -> int:
        return _EP_LUX

    def read_sensor(self):
        return self.tsl.get_last_reading() + self.offset

    def get_report_value(self):
        return self.str_2_decimals(self.last_reading)

    def configure(self, json_conf):
        super().configure(json_conf)
        self.tsl.set_sample_interval(self.min_interval)