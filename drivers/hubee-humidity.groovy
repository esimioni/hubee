metadata {
    definition (name: "Hubee Humidity Sensor", namespace: "edu", author: "Eduardo Simioni") {
        capability "Sensor"
        capability "Relative Humidity Measurement"
    }
}

#include edu.numeric-change-device
#include edu.zigbee-utils
#include edu.hubee-lib

def getEndpoint() {
    return EP_HUMIDITY
}

def getEventName() {
    return "humidity"
}

def getExtraConfig() {
    return ""
}