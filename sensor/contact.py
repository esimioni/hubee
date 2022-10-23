from machine import Pin

import hubee
from device import Device


class ContactSensor(Device):

    def __init__(self, pin_name: str):
        super().__init__()
        self.check_pin = Pin(pin_name, Pin.IN, Pin.PULL_UP)
        self.open = None
        self.open_state = 1

    def get_endpoint(self) -> int:
        return hubee.EP_CONTACT

    def send_status(self, is_open: bool):
        self.open = is_open
        self.transmit_status('open' if is_open else 'closed')

    def child_check_send_status(self, time_now: int):
        is_open = self._is_open()
        if is_open != self.open:
            self.send_status(is_open)

    def configure(self, json_conf: object):
        self.open_state = json_conf[hubee.P_OPEN_STATE]

    def _is_open(self) -> bool:
        return self.check_pin.value() == self.open_state