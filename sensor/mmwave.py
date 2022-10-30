import time
from sys import stdin

from sensor.presence import PresenceDevice

_EP_PRESENCE = const(0x02)
_P_RADAR = 'RA'


# Hi-Link HLK-LD1125H-24G mmWave Radar
class PresenceSensor(PresenceDevice):

    def __init__(self):
        super().__init__()
        self.config_timeout = 500

    def get_endpoint(self) -> int:
        return _EP_PRESENCE

    def is_present(self):
        # TODO: Use a pre-allocated buffer? https://docs.micropython.org/en/latest/reference/constrained.html#execution-phase
        read_bytes = stdin.buffer.read()
        if read_bytes is None:
            return False

        lines = read_bytes.split(b'\n')
        i = len(lines) - 1
        while i >= 0:
            line = lines[i].decode()
            if line.startswith('mov') or line.startswith('occ'):
                return True
            i = i - 1
        return False

    def configure(self, json_conf):
        super().configure(json_conf)
        for i in range(0x03):
            self._configure_radar_settings(json_conf[_P_RADAR] + ';save')

    def _configure_radar_settings(self, settings: str):
        for setting in settings.split(';'):
            self._configure_radar_setting(setting)

    def _configure_radar_setting(self, conf: str):
        self._flush_buffer()
        start = time.ticks_ms()
        print(conf + '\r')
        time.sleep_ms(30)
        while (time.ticks_ms() - start) <= self.config_timeout:
            read_bytes = stdin.buffer.read()
            if read_bytes is None:
                continue
            lines = read_bytes.split(b'\n')
            for line in lines:
                message = line.decode()
                if message.startswith('rmax') or message.startswith('mth') or message.startswith('all vars'):
                    return self.transmit_reply('Radar says: {}', message)

    def before_send_status(self):
        self._flush_buffer()

    def after_send_status(self):
        self._flush_buffer()

    def _flush_buffer(self):
        _ = stdin.buffer.read()