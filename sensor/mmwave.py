import gc
import time
from sys import stdin

import micropython
from machine import Pin

from sensor.presence import PresenceDevice

# mov and occ
_M = const(0x6D)
_O = const(0x6F)
_V = const(0x76)
_C = const(0x63)


# mmWave Radar -> Tested with Hi-Link HLK-LD1125H-24G, it might work with other models from Hi-Link
# PIR Motion Sensor (optional) -> Any PIR Motion Sensor with output signal between 0.7 and 3.5Vcc
class PresenceSensor(PresenceDevice):

    def __init__(self):
        # disables CTRL+C - Sometimes it is sent by the mmWave sensor and a KeyboardInterrupt (exception) is raised
        micropython.kbd_intr(-1)
        super().__init__()
        self.config_timeout = 500
        self.moving_only = False
        self.use_pir = False
        self.radar_configured = False
        self.pin = Pin('D12', Pin.IN, Pin.PULL_DOWN)  # PIR sensor read pin, XBee pin 4

    def get_endpoint(self) -> int:
        return 0x02  # _EP_PRESENCE

    def is_present(self):
        if self.use_pir:
            if not self.present:
                return self.is_present_pir()
            else:
                return self.is_present_mmwave() or self.is_present_pir()
        else:
            return self.is_present_mmwave()

    def is_present_pir(self):
        return self.pin.value() is 1

    def is_present_mmwave(self):
        # TODO: Use a pre-allocated buffer? https://docs.micropython.org/en/latest/reference/constrained.html#execution-phase
        read_bytes = stdin.buffer.read()
        if read_bytes is None or len(read_bytes) < 3:
            return False

        i = 0
        max_index = len(read_bytes) - 2
        while i < max_index:
            if (read_bytes[i] == _M or (not self.moving_only and read_bytes[i] == _O)) and i < max_index + 1:
                if (read_bytes[i + 1] == _O and read_bytes[i + 2] == _V) \
                        or (not self.moving_only and read_bytes[i + 1] == _C and read_bytes[i + 2] == _C):
                    return True
            i += 1

    def configure(self, json_conf):
        # self.transmit_reply('Starting module configuration')
        super().configure(json_conf)
        self.moving_only = json_conf['MO']
        self.use_pir = json_conf['PI']
        sleep_period = 1000

        # self.transmit_reply('Radar configuration started')
        for i in range(13):
            time.sleep_ms(sleep_period)
            # self.transmit_reply('Sleeping for {}ms', sleep_period)
            self._configure_radar_settings(json_conf['RA'] + ';save')
            sleep_period = int(sleep_period * 1.2)
            if self.radar_configured:
                return True

        return False

    def _configure_radar_settings(self, settings: str):
        for setting in settings.split(';'):
            self._configure_radar_setting(setting)

    def _configure_radar_setting(self, conf: str):
        time.sleep_ms(250)
        self._flush_buffer()
        start = time.ticks_ms()
        print(conf + '\r')
        time.sleep_ms(30)
        while time.ticks_diff(time.ticks_ms(), start) <= self.config_timeout:
            read_bytes = stdin.buffer.read()
            if read_bytes is None:
                continue
            lines = read_bytes.split(b'\n')
            for line in lines:
                message = line.decode()
                if message.startswith('rmax') or message.startswith('mth') or message.startswith('all vars') or message.startswith('received'):
                    self.transmit_reply('Radar says: {}', message)
                    self.radar_configured = True

    def before_send_status(self):
        self._flush_buffer()

    def after_send_status(self):
        self._flush_buffer()

    def _flush_buffer(self):
        stdin.buffer.read()
        gc.collect()