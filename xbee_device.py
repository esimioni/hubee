import gc
import time

import xbee

import hubee
from device import NumericChangeDevice
from zigbee import Zigbee

_BLE_ON_PERIOD = const(600000)  # 10 minutes


class XBeeDevice(NumericChangeDevice):

    def __init__(self):
        super().__init__()
        self.ble_on_since = 0

    def get_endpoint(self) -> int:
        return 0x01  # _EP_XBEE

    def start(self, zigbee: Zigbee):
        super().start(zigbee)
        self._ble_on_off(True)

    def read_sensor(self):
        return xbee.atcmd('TP')

    def get_report_value(self):
        # "voltage|free.mem|rssi|firmware|temperature|software
        gc.collect()
        mem_free = gc.mem_free()
        return '{}|{}|{}|{}|{}|{}'.format(self._read_voltage(), mem_free, xbee.atcmd('DB'), hex(xbee.atcmd('VR'))[0x02:].upper(),
                                          self.last_reading, hubee.SW_VER)

    def _read_voltage(self):
        voltage = str(xbee.atcmd('%V'))
        return float('{}.{}'.format(voltage[0:1], voltage[1:3]))

    def _ble_on_off(self, on: bool):
        xbee.atcmd('BT', 1 if on else 0)
        self.ble_on_since = time.ticks_ms() if on else 0
        self.transmit_reply('Bluetooth {}', 'on' if on else 'off')

    def ble_disable(self):
        if self.ble_on_since > 0 and hubee.interval_expired(time.ticks_ms(), self.ble_on_since, _BLE_ON_PERIOD):
            self._ble_on_off(False)

    def _module_set_name(self, name: str):
        xbee.atcmd('NI', name)
        xbee.atcmd('BI', name)

    def _join_disable(self):
        xbee.atcmd('JV', 0)
        xbee.atcmd('JN', 0)

    def configure(self, json_conf):
        super().configure(json_conf)
        self._module_set_name(json_conf['NA'])
        self._join_disable()
        xbee.atcmd('WR')
        return True