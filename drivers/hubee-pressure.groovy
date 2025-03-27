metadata {
    definition (name: 'Hubee Pressure Sensor', namespace: 'edu', author: 'Eduardo Simioni') {
        capability 'Sensor'
        capability 'Pressure Measurement'
    }
}

#include edu.numeric-change-device
#include edu.zigbee-utils
#include edu.hubee-lib

def getEndpoint() {
    return EP_PRESSURE
}

def getEventName() {
    return 'pressure'
}

def getEventFormats() {
    return '%s hPa'
}

def getExtraConfig() {
    return ''
}