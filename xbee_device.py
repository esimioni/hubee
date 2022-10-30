import time

import machine
import xbee

from device import NumericChangeDevice
from zigbee import Zigbee

# @formatter:off
_EP_XBEE          = const(0x01)
_BLE_ON_PERIOD    = const(600000)  # 10 minutes
_IN_CMD_REBOOT    = '01'
_IN_CMD_ENABLE_BT = '03'
_P_NAME           = 'NA'
# @formatter:on


class XBeeDevice(NumericChangeDevice):

    def __init__(self):
        super().__init__()
        self.ble_on = False
        self.ble_on_since = 0x00

    def get_endpoint(self) -> int:
        return _EP_XBEE

    def start(self, zigbee: Zigbee):
        super().start(zigbee)

    def read_sensor(self):
        voltage = str(xbee.atcmd('%V'))
        return float('{}.{}'.format(voltage[0:1], voltage[1:3]))

    def get_report_value(self):
        return str(self.last_reading)

    def _ble_setup(self):
        self._ble_set_name()

    def _ble_set_name(self):
        xbee.atcmd('BI', self._module_get_name())

    def _ble_on_off(self, on: bool):
        xbee.atcmd('BT', 0x01 if on else 0x00)
        self.ble_on = on
        self.ble_on_since = time.ticks_ms() if on else 0x00
        self.transmit_reply('Bluetooth {}', 'on' if on else 'off')

    def ble_disable(self):
        if self.ble_on and time.ticks_ms() - self.ble_on_since >= _BLE_ON_PERIOD:
            self._ble_on_off(False)

    def _module_set_name(self, name: str):
        xbee.atcmd('NI', name[0:20])
        self._ble_setup()

    def _module_get_name(self) -> str:
        return xbee.atcmd('NI')

    def _join_disable(self):
        xbee.atcmd('JV', 0x00)
        xbee.atcmd('JN', 0x00)

    def child_handle_command(self, command: str, payload: str):
        if command == _IN_CMD_REBOOT:
            self.transmit_reply('Rebooting XBee...')
            machine.reset()
        elif command == _IN_CMD_ENABLE_BT:
            self._ble_on_off(True)

    def configure(self, json_conf):
        super().configure(json_conf)
        self._module_set_name(json_conf[_P_NAME])
        self._join_disable()