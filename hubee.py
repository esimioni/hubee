# @formatter:off
IS_PROD          = True  # TODO: parameterize?
BLE_ON_PERIOD    = const(600000)  # 10 minutes
BLE_ALWAYS_ON    = not IS_PROD
_DEBUG           = not IS_PROD

EP_XBEE          = const(0x01)
EP_PRESENCE      = const(0x02)
EP_CONTACT       = const(0x03)
EP_TEMPERATURE   = const(0x04)
EP_HUMIDITY      = const(0x05)
EP_PRESSURE      = const(0x06)
EP_AIR_QUALITY   = const(0x07)
EP_ILLUMINANCE   = const(0x08)
EP_PROXIMITY     = const(0x09)

IN_CMD_REBOOT    = '01'
IN_CMD_ENABLE_BT = '03'

CMD_STATUS       = '01'
CMD_CONFIG       = '02'
CMD_STARTED      = '03'
CMD_REPLY        = '04'
CMD_UNKNOWN      = '88'
CMD_INFO         = '97'
CMD_WARN         = '98'
CMD_ERROR        = '99'

P_NAME           = 'NA'
P_FIXED          = 'FI'
P_SCALE          = 'SC'
P_RADAR          = 'RA'
P_OFFSET         = 'OF'
P_AMOUNT         = 'AM'
P_TIMEOUT        = 'TO'
P_DISTANCE       = 'DI'
P_OPEN_STATE     = 'OS'
P_MIN_INTERVAL   = 'MI'
P_MAX_INTERVAL   = 'MA'
# @formatter:on


def debug(message: str, endpoint: int = None, *args):
    if _DEBUG:
        prefix = '' if endpoint is None else '-- EP {} debug    '.format(endpoint)
        print(prefix + message.format(*args))


def str_2_decimals(value) -> str:
    return "{:.2f}".format(value)