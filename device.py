import gc
import json

import hubee
from zigbee import Zigbee


# _CMD_STATUS  = '01'
# _CMD_CONFIG  = '02'
# _CMD_STARTED = '03'
# _CMD_REPLY   = '04'
# _CMD_UNKNOWN = '88'
# _CMD_INFO    = '97'
# _CMD_WARN    = '98'
# _CMD_ERROR   = '99'

class Device:

    def __init__(self):
        gc.collect()
        self.zigbee = None
        self.configured = False

    def check_send_status(self, time_now: int):
        if self.configured:
            self.child_check_send_status(time_now)

    def start(self, zigbee: Zigbee):
        self.zigbee = zigbee
        self._transmit('03', 'Device on endpoint {:02X} started', self.get_endpoint())
        self._config_start()

    def _config_start(self):
        self._transmit('02', 'Send me my config')

    def handle_command(self, command: str, payload: str):
        if command == '02':
            self._load_config(payload)
        else:
            self.child_handle_command(command, payload)

    def _load_config(self, payload: str):
        self.configured = self.configure(json.loads(payload))
        if self.configured:
            self.transmit_info('Endpoint {:02X} configured', self.get_endpoint())
        else:
            self.transmit_error('Endpoint {:02X} configuration failed', self.get_endpoint())

    def child_handle_command(self, command: str, payload: str):
        self.handle_unknown_command(command)

    def handle_unknown_command(self, command: str, endpoint: int = None, cluster: int = None, payload: str = None):
        actual_endpoint = endpoint if self.get_endpoint() is None else endpoint
        # 255 is broadcast and 0 is ZDO (stack level), ignoring
        if 255 > endpoint > 0:
            self.transmit_error('UNKcmd EP{:02X} CM{} CL{} {}', actual_endpoint, command, cluster,
                                self._filter_non_printable(payload))

    def _filter_non_printable(self, text: str):
        return ''.join([s for s in text.strip() if ord(s) < 127])

    def transmit_status(self, status: str, *args):
        self._transmit('01', status, *args)

    def transmit_reply(self, message: str, *args):
        self._transmit('04', message, *args)

    def transmit_warn(self, message: str, *args):
        self._transmit('98', message, *args)

    def transmit_info(self, message: str, *args):
        self._transmit('97', message, *args)

    def transmit_error(self, message: str, *args):
        self._transmit('99', message, *args)

    def _transmit(self, command: str, payload: str, *args):
        self.zigbee.transmit(self.get_endpoint(), command, payload, *args)

    def _str_2_decimals(self, value) -> str:
        return "{:.2f}".format(value)

    def child_check_send_status(self, time_now: int):
        raise NotImplementedError

    def configure(self, json_conf):
        raise NotImplementedError

    def get_endpoint(self) -> int:
        raise NotImplementedError


class PeriodicDevice(Device):

    def __init__(self):
        super().__init__()
        self.last_report_time = None
        self.min_interval = None

    def _set_min_interval(self, value: int):
        self.min_interval = value * 1000

    def child_check_send_status(self, time_now: int):
        if self.min_interval_expired(time_now):
            self.do_report(time_now)

    def do_report(self, time_now):
        self._report()
        self.last_report_time = time_now

    def min_interval_expired(self, time_now):
        return hubee.interval_expired(time_now, self.last_report_time, self.min_interval)

    def configure(self, json_conf: object):
        self._set_min_interval(json_conf['MI'])
        return True

    def _report(self):
        self.transmit_status(self.get_report_value())

    def get_report_value(self):
        raise NotImplementedError


class NumericChangeDevice(PeriodicDevice):

    def __init__(self):
        super().__init__()
        self.offset = None
        self.last_reported_value = None
        self.max_interval = None
        self.change_amount = None
        self.fixed_value = None
        self.last_reading = None

    def _set_max_interval(self, value: int):
        self.max_interval = value * 1000

    def child_check_send_status(self, time_now: int):
        if self.min_interval_expired(time_now):
            self.last_reading = self.read_sensor() + self.offset
            if self._should_report(time_now):
                self.last_reported_value = self.last_reading
                self.do_report(time_now)

    def _should_report(self, time_now: int) -> bool:
        if self._max_interval_expired(time_now) or self.last_reported_value is None:
            return True

        diff = abs(self.last_reading - self.last_reported_value)
        if diff == 0:
            return False

        if self.fixed_value:
            return diff >= self.change_amount

        if self.last_reported_value == 0:
            return True

        percentage_change = abs(diff / self.last_reported_value * 100)
        return percentage_change >= self.change_amount

    def _max_interval_expired(self, time_now):
        return hubee.interval_expired(time_now, self.last_report_time, self.max_interval)

    def configure(self, json_conf):
        super().configure(json_conf)
        self.offset = json_conf['OF']
        self.fixed_value = json_conf['FI']
        self.change_amount = json_conf['AM']
        self._set_max_interval(json_conf['MA'])
        return True

    def read_sensor(self):
        raise NotImplementedError