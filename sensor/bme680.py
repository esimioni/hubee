import time

from ustruct import unpack

# @formatter:off
_COEFF_ADDR1     = const(0x89)
_COEFF_ADDR2     = const(0xE1)
_RES_HEAT_0      = const(0x5A)
_GAS_WAIT_0      = const(0x64)
_REG_SOFTRESET   = const(0xE0)
_REG_CTRL_GAS    = const(0x71)
_REG_CTRL_HUM    = const(0x72)
_REG_CTRL_MEAS   = const(0x74)
_REG_CONF        = const(0x75)
_REG_MEAS_STATUS = const(0x1D)
_RUNGAS          = const(0x10)

_LOOKUP_TB_1 = (
    2147483647.0,
    2147483647.0,
    2147483647.0,
    2147483647.0,
    2147483647.0,
    2126008810.0,
    2147483647.0,
    2130303777.0,
    2147483647.0,
    2147483647.0,
    2143188679.0,
    2136746228.0,
    2147483647.0,
    2126008810.0,
    2147483647.0,
    2147483647.0,
)

_LOOKUP_TB_2 = (
    4096000000.0,
    2048000000.0,
    1024000000.0,
    512000000.0,
    255744255.0,
    127110228.0,
    64000000.0,
    32258064.0,
    16016016.0,
    8000000.0,
    4000000.0,
    2000000.0,
    1000000.0,
    500000.0,
    250000.0,
    125000.0,
)
# @formatter:on


# Taken from: https://github.com/adafruit/Adafruit_CircuitPython_BME680/blob/main/adafruit_bme680.py
class AdfBME680:

    # refresh_rate: Maximum number of readings per second. Faster property reads will be from the previous reading.
    def __init__(self, refresh_rate: int):
        self._write(_REG_SOFTRESET, [0xB6])
        time.sleep_ms(5)
        self._read_calibration()
        self._write(_RES_HEAT_0, [0x73])
        self._write(_GAS_WAIT_0, [0x65])
        self._pres_oversample = 0b011
        self._temp_oversample = 0b100
        self._hum_oversample = 0b010
        self._filter = 0b010
        self._adc_pres = None
        self._adc_temp = None
        self._adc_hum = None
        self._adc_gas = None
        self._gas_range = None
        self._t_fine = None
        self._last_reading = 0
        self._min_refresh_time = 1000 / refresh_rate

    @property
    def temperature(self):
        self._perform_reading()
        calc_temp = ((self._t_fine * 5) + 128) / 256
        return calc_temp / 100

    @property
    def pressure(self):
        self._perform_reading()
        var1 = (self._t_fine / 2) - 64000
        var2 = ((var1 / 4) * (var1 / 4)) / 2048
        var2 = (var2 * self._pres_calibration[5]) / 4
        var2 = var2 + (var1 * self._pres_calibration[4] * 2)
        var2 = (var2 / 4) + (self._pres_calibration[3] * 65536)
        var1 = ((((var1 / 4) * (var1 / 4)) / 8192) * (self._pres_calibration[2] * 32) / 8) + (
                (self._pres_calibration[1] * var1) / 2)
        var1 = var1 / 262144
        var1 = ((32768 + var1) * self._pres_calibration[0]) / 32768
        calc_pres = 1048576 - self._adc_pres
        calc_pres = (calc_pres - (var2 / 4096)) * 3125
        calc_pres = (calc_pres / var1) * 2
        var1 = (self._pres_calibration[8] * (((calc_pres / 8) * (calc_pres / 8)) / 8192)) / 4096
        var2 = ((calc_pres / 4) * self._pres_calibration[7]) / 8192
        var3 = (((calc_pres / 256) ** 3) * self._pres_calibration[9]) / 131072
        calc_pres += (var1 + var2 + var3 + (self._pres_calibration[6] * 128)) / 16
        return calc_pres / 100

    @property
    def humidity(self):
        self._perform_reading()
        temp_scaled = ((self._t_fine * 5) + 128) / 256
        var1 = (self._adc_hum - (self._hum_calibration[0] * 16)) - ((temp_scaled * self._hum_calibration[2]) / 200)
        var2 = (self._hum_calibration[1] * (((temp_scaled * self._hum_calibration[3]) / 100) + (
                ((temp_scaled * ((temp_scaled * self._hum_calibration[4]) / 100)) / 64) / 100) + 16384)) / 1024
        var3 = var1 * var2
        var4 = self._hum_calibration[5] * 128
        var4 = (var4 + ((temp_scaled * self._hum_calibration[6]) / 100)) / 16
        var5 = ((var3 / 16384) * (var3 / 16384)) / 1024
        var6 = var4 * var5 / 2
        calc_hum = (((var3 + var6) / 1024) * 1000) / 4096
        calc_hum /= 1000
        if calc_hum > 100:
            calc_hum = 100
        elif calc_hum < 0:
            calc_hum = 0
        return calc_hum

    @property
    def gas(self):
        self._perform_reading()
        var1 = ((1340 + (5 * self._sw_err)) * _LOOKUP_TB_1[self._gas_range]) / 65536
        var2 = (self._adc_gas * 32768 - 16777216) + var1
        var3 = _LOOKUP_TB_2[self._gas_range] * var1 / 512
        calc_gas_res = (var3 + (var2 / 2)) / var2
        return int(calc_gas_res)

    def _perform_reading(self):
        if time.ticks_diff(self._last_reading, time.ticks_ms()) * time.ticks_diff(0, 1) < self._min_refresh_time:
            return
        self._write(_REG_CONF, [self._filter << 2])
        self._write(_REG_CTRL_MEAS, [(self._temp_oversample << 5) | (self._pres_oversample << 2)])
        self._write(_REG_CTRL_HUM, [self._hum_oversample])
        self._write(_REG_CTRL_GAS, [_RUNGAS])
        ctrl = self._read_byte(_REG_CTRL_MEAS)
        ctrl = (ctrl & 0xFC) | 0x01
        self._write(_REG_CTRL_MEAS, [ctrl])
        new_data = False
        while not new_data:
            data = self._read(_REG_MEAS_STATUS, 15)
            new_data = data[0] & 0x80 != 0
            time.sleep_ms(5)  # TODO: Try to avoid the sleep here. Enable and come back later to check?
        self._last_reading = time.ticks_ms()
        # noinspection PyUnboundLocalVariable
        self._adc_pres = self._read24(data[2:5]) / 16
        self._adc_temp = self._read24(data[5:8]) / 16
        self._adc_hum = unpack('>H', bytes(data[8:10]))[0]
        self._adc_gas = int(unpack('>H', bytes(data[13:15]))[0] / 64)
        self._gas_range = data[14] & 0x0F
        var1 = (self._adc_temp / 8) - (self._temp_calibration[0] * 2)
        var2 = (var1 * self._temp_calibration[1]) / 2048
        var3 = ((var1 / 2) * (var1 / 2)) / 4096
        var3 = (var3 * self._temp_calibration[2] * 16) / 16384
        self._t_fine = int(var2 + var3)

    def _read_calibration(self):
        coeff = self._read(_COEFF_ADDR1, 25)
        coeff += self._read(_COEFF_ADDR2, 16)
        coeff = list(unpack('<hbBHhbBhhbbHhhBBBHbbbBbHhbb', bytes(coeff[1:39])))
        coeff = [float(i) for i in coeff]
        self._temp_calibration = [coeff[x] for x in [23, 0, 1]]
        self._pres_calibration = [coeff[x] for x in [3, 4, 5, 7, 8, 10, 9, 12, 13, 14]]
        self._hum_calibration = [coeff[x] for x in [17, 16, 18, 19, 20, 21, 22]]
        self._gas_calibration = [coeff[x] for x in [25, 24, 26]]
        self._hum_calibration[1] *= 16
        self._hum_calibration[1] += self._hum_calibration[0] % 16
        self._hum_calibration[0] /= 16
        self._heat_range = (self._read_byte(0x02) & 0x30) / 16
        self._heat_val = self._read_byte(0x00)
        self._sw_err = (self._read_byte(0x04) & 0xF0) / 16

    def _read24(self, arr):
        ret = 0.0
        for b in arr:
            ret *= 256.0
            ret += float(b & 0xFF)
        return ret

    def _read_byte(self, register):
        return self._read(register, 1)[0]

    def _read(self, register, length):
        raise NotImplementedError

    def _write(self, register, values):
        raise NotImplementedError


class BME680(AdfBME680):

    def __init__(self, i2c, refresh_rate = 0.1, address = 0x77):
        self._i2c = i2c
        self._address = address
        super().__init__(refresh_rate)

    def _read(self, register, length):
        res = bytearray(length)
        self._i2c.readfrom_mem_into(self._address, register & 0xff, res)
        return res

    def _write(self, register, values):
        for value in values:
            self._i2c.writeto_mem(self._address, register, bytearray([value & 0xff]))
            register += 1