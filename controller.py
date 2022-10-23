import time

from umachine import WDT

import hubee
from device import Device
from xbee_device import XBeeDevice
from zigbee import Zigbee


class Controller:

    def __init__(self, devices: list[Device]):
        self.wdt = WDT(timeout = (30000 if hubee.IS_PROD else 9999999))
        self.zigbee = Zigbee()
        self.xbee_device = XBeeDevice()
        self.devices = {}
        devices.append(self.xbee_device)
        self._setup(sorted(devices, key = lambda device: device.get_endpoint()))

    def _setup(self, devices: list[Device]):
        for device in devices:
            device.start(self.zigbee)
            self.devices[device.get_endpoint()] = device

    def _check_devices(self):
        time_now = time.ticks_ms()
        for device in self.devices.values():
            device.check_send_status(time_now)

    def _check_zigbee_cmd(self):
        zgb_msg = self.zigbee.receive()
        if zgb_msg:
            endp = zgb_msg['endpoint']
            cmd = zgb_msg['command']
            payld = zgb_msg['payload']
            device = self.devices.get(endp)
            if device:
                device.handle_command(cmd, payld)
            else:
                self.xbee_device.handle_unknown_command(cmd, endp)

    def run(self):
        while True:
            self.wdt.feed()
            self._check_devices()
            self._check_zigbee_cmd()
            self.xbee_device.ble_disable()