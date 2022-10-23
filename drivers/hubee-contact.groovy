metadata {
    definition (name: "Hubee Contact Sensor", namespace: "edu", author: "Eduardo Simioni") {
        capability "Sensor"
        capability "Contact Sensor"
    }
    preferences {
        input (name: "openState", type: "enum", title: "Open State", description: "", defaultValue: "1", options: ["1", "0"])
    }
}

#include edu.zigbee-utils
#include edu.hubee-lib

def getEndpoint() {
    return EP_CONTACT
}

def getEventName() {
    return "contact"
}

def getConfigPayload() {
    return "{\"${PRM_OPEN_STATE}\":${openState}}"
}