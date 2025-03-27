import gc
import io
import sys

from zigbee import Zigbee


def notify_exception(ex: BaseException):
    gc.collect()
    strio = io.StringIO()
    gc.collect()
    sys.print_exception(ex, strio)
    gc.collect()
    lines = strio.getvalue().split('\n')
    gc.collect()
    i = len(lines) - 2
    gc.collect()
    zb = Zigbee()
    gc.collect()
    while i >= 0:
        line = lines[i].strip()
        if line.startswith('File'):
            line = line.rsplit('/')[-1]
            line = line[:line.find('"')] + ':' + line[line.find('"') + 8:]
        if not line.startswith('Trace'):
            zb.transmit(0x01, '99', line)
        i -= 1