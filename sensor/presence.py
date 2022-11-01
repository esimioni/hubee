import hubee
from device import Device
from zigbee import Zigbee

_P_TIMEOUT = 'TO'


class PresenceDevice(Device):

    def __init__(self):
        super().__init__()
        self.last_detected = 0x00
        self.timeout = None
        self.present = False

    def start(self, zigbee: Zigbee):
        super().start(zigbee)
        self.send_status(False)

    def send_status(self, present: bool):
        self.present = present
        self.before_send_status()
        self.transmit_status('present' if present else 'not present')
        self.after_send_status()

    def child_check_send_status(self, time_now: int):
        if self.is_present():
            self.last_detected = time_now
            if not self.present:
                self.send_status(True)
        elif self.present and hubee.interval_expired(time_now, self.last_detected, self.timeout):
            self.send_status(False)

    def configure(self, json_conf):
        self.timeout = json_conf[_P_TIMEOUT]

    def is_present(self):
        raise NotImplementedError

    def before_send_status(self):
        pass

    def after_send_status(self):
        pass