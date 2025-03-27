metadata {
    definition (name: 'Hubee Temperature Sensor', namespace: 'edu', author: 'Eduardo Simioni') {
        capability 'Sensor'
        capability 'Temperature Measurement'
    }
}

#include edu.numeric-change-device
#include edu.zigbee-utils
#include edu.hubee-lib

def getEndpoint() {
    return EP_TEMPERATURE
}

def getEventName() {
    return 'temperature'
}

def getEventFormats() {
    return '%s°' + getTemperatureScale()
}

def getExtraConfig() {
    return ",\"${PRM_SCALE}\":\"${getTemperatureScale()}\""
}