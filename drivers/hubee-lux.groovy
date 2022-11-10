metadata {
    definition (name: "Hubee Lux Sensor", namespace: "edu", author: "Eduardo Simioni") {
        capability "Sensor"
        capability "Illuminance Measurement"
    }
    preferences {
        input (name: "integrationTime", type: "enum", title: "Integration Time", description: "", defaultValue: 0, required: true,
               options: [[0:"100ms"],[1:"200ms"],[2:"300ms"],[3:"400ms"],[4:"500ms"],[5:"600ms"]])
        input (name: "gain", type: "enum", title: "Gain", description: "", defaultValue: 0, required: true,
               options: [[0:"Low"],[16:"Med"],[32:"High"],[48:"Max"]])
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
    return ",\"${PRM_INTEG_TIME}\":${integrationTime},\"${PRM_GAIN}\":${gain}"
}