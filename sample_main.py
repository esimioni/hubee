from umachine import I2C

from controller import Controller
from sensor.bme680 import BME680
from sensor.contact import ContactSensor
from sensor.environment import TemperatureSensor, HumiditySensor, AirQualitySensor, PressureSensor
from sensor.lux import Tsl2591, LuxSensor
from sensor.presence import PresenceSensor
from sensor.presence import ProximitySensor

# import gc
# import micropython
# gc.collect()
# micropython.mem_info()
# micropython.qstr_info(1)

# def print_mf(step: str):
#     gc.collect()
#     print('Mem Free {}: {}'.format(step, gc.mem_free()))

i2c = I2C(1, freq = 400000)
bme = BME680(i2c)
tsl = Tsl2591(i2c)

# @formatter:off
contact     = ContactSensor('D0')  # Pin 20 -> AD0/DIO0/CB (callback)
presence    = PresenceSensor()
temperature = TemperatureSensor(bme)
humidity    = HumiditySensor(bme)
air_quality = AirQualitySensor(bme)
pressure    = PressureSensor(bme)
lux         = LuxSensor(tsl)
proximity   = ProximitySensor(i2c)
# @formatter:on

# If there is a single sensor use this syntax, with the comma: (bme,)
Controller([contact, presence, temperature, humidity, air_quality, pressure, lux, proximity], (bme, tsl)).run()