import time
import xbee
from umachine import I2C

import debug_utils
import hubee
from controller import Controller
from sensor.bme680 import BME680
from sensor.contact import ContactSensor
from sensor.environment import TemperatureSensor, HumiditySensor, AirQualitySensor, PressureSensor
from sensor.lux import Tsl2591, LuxSensor
from sensor.mmwave import PresenceSensor
from sensor.proximity import ProximitySensor

try:
    i2c = I2C(1, freq = 400000)
    bme = BME680(i2c)
    tsl = Tsl2591(i2c)

    # @formatter:off
    contact     = ContactSensor()
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
except BaseException as e:
    if hubee.IS_PROD:
        try:
            debug_utils.notify_exception(e)
        finally:
            time.sleep(10)
            xbee.atcmd('FR')
    else:
        raise