import binascii
import gc
import time

import xbee

import hubee


class Zigbee:

    def __init__(self):
        self._connect()

    def _connect(self):
        while xbee.atcmd('AI') != 0x00:
            time.sleep_ms(50)

    def transmit(self, endpoint: int, command: str, payload: str, *args):
        gc.collect()
        payld_fttd = payload.format(*args)
        self.debug('<< EP {} sending  {}: {}', None, endpoint, command, payld_fttd)
        hex_payld = binascii.hexlify(payld_fttd)
        tx_req = '{}{}{}{}{}'.format('7E00', self._msg_len(hex_payld), '2D', command, hex_payld.decode())
        xbee.transmit(xbee.ADDR_COORDINATOR, binascii.unhexlify(tx_req), source_ep = endpoint, dest_ep = endpoint)

    def _msg_len(self, msg: bytes):
        res = 0x02 + len(msg)
        return '{:0>2}'.format(res)

    def debug(self, message: str, endpoint: int = None, *args):
        if not hubee.IS_PROD:
            prefix = '' if endpoint is None else '-- EP {} debug    '.format(endpoint)
            print(prefix + message.format(*args))

    def receive(self) -> dict[str, object]:
        msg = xbee.receive()
        if msg:
            gc.collect()
            res = {
                'endpoint': msg['dest_ep'],
                'command' : binascii.hexlify(msg['payload'][2:3]).decode(),
                'payload' : msg['payload'][3:].decode()
            }
            self.debug('>> EP {} received {}: {}', None, res['endpoint'], res['command'], res['payload'])
            return res
        else:
            return