import binascii
import gc
import time

import xbee


# import hubee


class Zigbee:

    def __init__(self):
        self.connect()

    def connect(self):
        while xbee.atcmd('AI') != 0:
            time.sleep_ms(50)

    def transmit(self, endpoint: int, command: str, payload: str, *args):
        gc.collect()
        payld_fttd = payload.format(*args)
        # self.debug('<< EP {:02X} sending  {}: {}', None, endpoint, command, payld_fttd)
        # 7E - Start Delimiter of XBee API Frame - Always 7E.
        # 2D - Frame type - User Data Relay
        # Message length plus 2, counting the 2 previous bytes
        prefix = '7E{:0>4}2D{}'.format((2 + len(payld_fttd) * 2), command)
        xbee.transmit(xbee.ADDR_COORDINATOR, binascii.unhexlify(prefix) + payld_fttd.encode(), source_ep = endpoint, dest_ep = endpoint)
        gc.collect()

    # def debug(self, message: str, endpoint: int = None, *args):
    #     if not hubee.IS_PROD:
    #         prefix = '' if endpoint is None else '-- EP {:02X} debug    '.format(endpoint)
    #         print(prefix + message.format(*args))

    def receive(self) -> dict[str, object]:
        msg = xbee.receive()
        if msg:
            gc.collect()
            res = {
                'endpoint': msg['dest_ep'],
                'command' : binascii.hexlify(msg['payload'][2:3]).decode(),
                'payload' : msg['payload'][3:].decode(),
                'cluster' : msg['cluster']
            }
            # self.debug('>> EP {:02X} received {}: {}', None, res['endpoint'], res['command'], res['payload'])
            return res
        else:
            return