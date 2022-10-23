metadata {
    definition (name: "Hubee Air Quality Sensor", namespace: "edu", author: "Eduardo Simioni") {
        capability "Sensor"
        capability "Air Quality"
    }
}

#include edu.numeric-change-device
#include edu.zigbee-utils
#include edu.hubee-lib

def getEndpoint() {
    return EP_AIR_QUALITY
}

def getEventName() {
    return "airQualityIndex"
}

def getExtraConfig() {
    return ""
}