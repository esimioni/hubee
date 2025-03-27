from machine import Pin

from sensor.presence import PresenceDevice

# Any PIR Motion Sensor with output signal between 0.7 and 3.5Vcc
class PirSensor(PresenceDevice):

    def __init__(self):
        super().__init__()
        self.pin = Pin('D12', Pin.IN, Pin.PULL_UP)

    def get_endpoint(self) -> int:
        return 0x0A  #EP_PIR

    def is_present(self):
        return self.pin.value() is 1