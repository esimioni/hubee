metadata {
    definition (name: "Hubee Lux Sensor", namespace: "edu", author: "Eduardo Simioni") {
        capability "Sensor"
        capability "Illuminance Measurement"
    }
}

#include edu.numeric-change-device
#include edu.zigbee-utils
#include edu.hubee-lib

def getEndpoint() {
    return EP_ILLUMINANCE
}

def getEventName() {
    return "illuminance"
}

def getExtraConfig() {
    return ""
}