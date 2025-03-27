import hubee


class Sensor:

    def reset_error(self):
        self.error_start_time = None

    def report_error(self, time_now: int) -> bool:
        if self.error_start_time is None:
            self.error_start_time = time_now

        return hubee.interval_expired(time_now, self.error_start_time, 600_000)

    def check(self):
        raise NotImplementedError