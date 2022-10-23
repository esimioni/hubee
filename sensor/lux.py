import time

import hubee
from device import NumericChangeDevice

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


class Tsl2591:

    def __init__(self, i2c, integration = _INTTIME_100MS, gain = _GAIN_LOW):
        self.bus = SMBusEmulator(i2c)
        self.integ_time = integration
        self.set_gain(gain)
        self.set_timing(self.integ_time)
        self._disable()

    def set_timing(self, integration):
        self._enable()
        self.integ_time = integration
        self.bus.write_byte_data(
            _SENSOR_ADDR,
            _CMD_BIT | _REG_CTRL,
            self.integ_time | self.gain
        )
        self._disable()

    def set_gain(self, gain):
        self._enable()
        self.gain = gain
        self.bus.write_byte_data(
            _SENSOR_ADDR,
            _CMD_BIT | _REG_CTRL,
            self.integ_time | self.gain
        )
        self._disable()

    def _calculate_lux(self, full, ir):
        if full == 0xFFFF | ir == 0xFFFF:
            return 0x00

        atime = _CASE_INTEG[self.integ_time]
        again = _CASE_GAIN[self.gain]

        cpl = atime * again / _LUX_DF
        lux1 = (full - (_LUX_COEFB * ir)) / cpl
        lux2 = ((_LUX_COEFC * full) - (_LUX_COEFD * ir)) / cpl
        return max([lux1, lux2])

    def _enable(self):
        self.bus.write_byte_data(_SENSOR_ADDR, _CMD_BIT | _REG_ENABLE, _ENABLE_PWRON | _ENABLE_AEN | _ENABLE_AIEN)

    def _disable(self):
        self.bus.write_byte_data(_SENSOR_ADDR, _CMD_BIT | _REG_ENABLE, _ENABLE_PWROFF)

    def _get_full_luminosity(self):
        self._enable()
        # TODO: Cannot sleep this much here, enable and come back later to check
        time.sleep(int(0.120 * self.integ_time + 0x01))
        full = self.bus.read_word_data(_SENSOR_ADDR, _CMD_BIT | _REG_CHAN0_LOW)
        ir = self.bus.read_word_data(_SENSOR_ADDR, _CMD_BIT | _REG_CHAN1_LOW)
        self._disable()
        return full, ir

    def sample(self):
        full, ir = self._get_full_luminosity()
        return self._calculate_lux(full, ir)


class LuxSensor(NumericChangeDevice):

    def __init__(self, tsl: Tsl2591):
        super().__init__()
        self.tsl = tsl

    def get_endpoint(self) -> int:
        return hubee.EP_ILLUMINANCE

    def read_sensor(self):
        return self.tsl.sample() + self.offset

    def _report(self):
        self.transmit_status(hubee.str_2_decimals(self.last_reading))