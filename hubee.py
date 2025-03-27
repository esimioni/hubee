import time

IS_PROD = True
SW_VER = '1.0.0'


def interval_expired(time_now: int, time_ref: int, interval: int) -> bool:
    if time_ref is None:
        return True

    return time.ticks_diff(time_now, time_ref) >= interval

# Just for reference. Moved to the modules to save RAM.
# EP_XBEE        = const(0x01)
# EP_PRESENCE    = const(0x02)
# EP_CONTACT     = const(0x03)
# EP_TEMPERATURE = const(0x04)
# EP_HUMIDITY    = const(0x05)
# EP_PRESSURE    = const(0x06)
# EP_AIR_QUALITY = const(0x07)
# EP_ILLUMINANCE = const(0x08)
# EP_PROXIMITY   = const(0x09)