from machine import Pin

from device import Device


class ContactSensor(Device):

    def __init__(self):
        super().__init__()
        self.check_pin = Pin('D11', Pin.IN, Pin.PULL_UP)  # XBee pin 7
        self.open = None
        self.open_state = 1

    def get_endpoint(self) -> int:
        return 0x03  # _EP_CONTACT

    def send_status(self, is_open: bool):
        self.open = is_open
        self.transmit_status('open' if is_open else 'closed')

    def child_check_send_status(self, time_now: int):
        is_open = self._is_open()
        if is_open != self.open:
            self.send_status(is_open)

    def configure(self, json_conf):
        self.open_state = json_conf['OS']

    def _is_open(self) -> bool:
        return self.check_pin.value() == self.open_state