metadata {
    definition (name: "Hubee Presence Sensor", namespace: "edu", author: "Eduardo Simioni") {
        capability "Sensor"
        capability "Presence Sensor"
    }
    preferences {
        input (name: "timeout", type: "number", title: "Timeout", description: "In milliseconds", defaultValue: "5000", range: "1..*", required: true)
        input (name: "rmax", type: "decimal", title: "Range", description: "Max detection distance in meters, one decimal place can be used", defaultValue: "6.0", range: "1..12", required: true)
        input (name: "mth1", type: "number", title: "mth1", description: "Sensitivity within 2.8 meters (lower = more sensitive)", defaultValue: "60", range: "0..*", required: true)
        input (name: "mth2", type: "number", title: "mth2", description: "Sensitivity in 2.8-8 meters range (lower = more sensitive)", defaultValue: "30", range: "0..*", required: true)
        input (name: "mth3", type: "number", title: "mth3", description: "Sensitivity beyond 8 meters (lower = more sensitive)", defaultValue: "20", range: "0..*", required: true)
    }
}

#include edu.zigbee-utils
#include edu.hubee-lib

def getEndpoint() {
    return EP_PRESENCE
}

def getEventName() {
    return "presence"
}

def getConfigPayload() {
    return "{\"${PRM_TIMEOUT}\":${timeout},\"${PRM_RADAR}\":\"rmax=${rmax};mth1=${mth1};mth2=${mth2};mth3=${mth3}\"}"
}