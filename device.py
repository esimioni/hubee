import gc
import json

import hubee
from zigbee import Zigbee

# @formatter:off
_CMD_STATUS     = '01'
_CMD_CONFIG     = '02'
_CMD_STARTED    = '03'
_CMD_REPLY      = '04'
_CMD_UNKNOWN    = '88'
_CMD_INFO       = '97'
_CMD_WARN       = '98'
_CMD_ERROR      = '99'

_P_FIXED        = 'FI'
_P_OFFSET       = 'OF'
_P_AMOUNT       = 'AM'
_P_MIN_INTERVAL = 'MI'
_P_MAX_INTERVAL = 'MA'
# @formatter:on


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
        self._transmit(_CMD_STARTED, 'Device on endpoint {} started', self.get_endpoint())
        self._config_start()

    def _config_start(self):
        self._transmit(_CMD_CONFIG, 'Send me my config')

    def handle_command(self, command: str, payload: str):
        if command == _CMD_CONFIG:
            self._load_config(payload)
        else:
            self.child_handle_command(command, payload)

    def _load_config(self, payload: str):
        self.configure(json.loads(payload))
        suffix = '' if self.configured else ', can now start reporting'
        self.configured = True
        self.transmit_info('Endpoint {} configured{}', self.get_endpoint(), suffix)
        gc.collect()

    def child_handle_command(self, command: str, payload: str):
        self.handle_unknown_command(command)

    def handle_unknown_command(self, command: str, endpoint: int = None):
        actual_endpoint = endpoint if self.get_endpoint() is None else endpoint
        self._transmit(_CMD_ERROR, 'Unknown cmd: EP: {}, CMD: {}', actual_endpoint, command)

    def transmit_status(self, status: str, *args):
        self._transmit(_CMD_STATUS, status, *args)

    def transmit_reply(self, message: str, *args):
        self._transmit(_CMD_REPLY, message, *args)

    def transmit_warn(self, message: str, *args):
        self._transmit(_CMD_WARN, message, *args)

    def transmit_info(self, message: str, *args):
        self._transmit(_CMD_INFO, message, *args)

    def _transmit(self, command: str, payload: str, *args):
        self.zigbee.transmit(self.get_endpoint(), command, payload, *args)

    def str_2_decimals(self, value) -> str:
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
        self._set_min_interval(json_conf[_P_MIN_INTERVAL])

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
            self.last_reading = self.read_sensor()
            if self._should_report(time_now):
                self.last_reported_value = self.last_reading
                self.do_report(time_now)

    def _should_report(self, time_now: int) -> bool:
        if self._max_interval_expired(time_now) or self.last_reported_value is None:
            return True

        diff = abs(self.last_reading - self.last_reported_value)
        if diff == 0x00:
            return False

        if self.fixed_value:
            return diff >= self.change_amount

        if self.last_reported_value == 0x00:
            return True

        percentage_change = abs(diff / self.last_reported_value * 100)
        return percentage_change >= self.change_amount

    def _max_interval_expired(self, time_now):
        return hubee.interval_expired(time_now, self.last_report_time, self.max_interval)

    def configure(self, json_conf):
        super().configure(json_conf)
        self.offset = json_conf[_P_OFFSET]
        self.fixed_value = json_conf[_P_FIXED]
        self.change_amount = json_conf[_P_AMOUNT]
        self._set_max_interval(json_conf[_P_MAX_INTERVAL])

    def read_sensor(self):
        raise NotImplementedError