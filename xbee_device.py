import time

import machine
import xbee

import hubee
from device import NumericChangeDevice
from zigbee import Zigbee

_RESET_CAUSE = {
    3 : 'HARD_RESET',
    4 : 'PWRON_RESET',
    5 : 'WDT_RESET',
    6 : 'SOFT_RESET',
    9 : 'LOCKUP_RESET',
    11: 'BROWNOUT_RESET',
}


class XBeeDevice(NumericChangeDevice):

    def __init__(self):
        super().__init__()
        self.ble_always_on = hubee.BLE_ALWAYS_ON
        self.ble_on = hubee.BLE_ALWAYS_ON
        self.ble_on_since = 0x00

    def get_endpoint(self) -> int:
        return hubee.EP_XBEE

    def start(self, zigbee: Zigbee):
        super().start(zigbee)
        self.transmit_info('Reset cause: {}'.format(_RESET_CAUSE[machine.reset_cause()]))

    def read_sensor(self):
        voltage = str(xbee.atcmd('%V'))
        return float('{}.{}'.format(voltage[0:1], voltage[1:3]))

    def get_report_value(self):
        return str(self.last_reading)

    def _ble_setup(self):
        self._ble_set_name()
        self._ble_on_off(self.ble_always_on)

    def _ble_set_name(self):
        xbee.atcmd('BI', self._module_get_name())

    def _ble_on_off(self, on: bool):
        if self.ble_on and on:
            return self.transmit_warn('Bluetooth already on')

        xbee.atcmd('BT', 0x01 if on else 0x00)
        self.ble_on = on
        self.ble_on_since = time.ticks_ms() if on else 0x00
        self.transmit_reply('Bluetooth {}', 'on' if on else 'off')

    def ble_disable(self):
        if not self.ble_always_on and self.ble_on and time.ticks_ms() - self.ble_on_since >= hubee.BLE_ON_PERIOD:
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
        if command == hubee.IN_CMD_REBOOT:
            self.transmit_reply('Rebooting XBee...')
            machine.reset()
        elif command == hubee.IN_CMD_ENABLE_BT:
            self._ble_on_off(True)

    def configure(self, json_conf: object):
        super().configure(json_conf)
        self._module_set_name(json_conf[hubee.P_NAME])
        self._join_disable()