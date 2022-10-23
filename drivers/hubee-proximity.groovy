metadata {
    definition (name: "Hubee Proximity Sensor", namespace: "edu", author: "Eduardo Simioni") {
        capability "Sensor"
        capability "Presence Sensor"
    }
    preferences {
        input (name: "timeout", type: "number", title: "Timeout", description: "In milliseconds", defaultValue: "5000", range: "1..*", required: true)
        input (name: "triggerDistance", type: "number", title: "Minimum trigger distance", description: "In milimeters", defaultValue: "300", range: "1..*", required: true)
    }
}

#include edu.zigbee-utils
#include edu.hubee-lib

def getEndpoint() {
    return EP_PROXIMITY
}

def getEventName() {
    return "presence"
}

def getConfigPayload() {
    return "{\"${PRM_TIMEOUT}\":${timeout},\"${PRM_DISTANCE}\":${triggerDistance}}"
}