metadata {
    definition (name: 'Hubee PIR Motion Sensor', namespace: 'edu', author: 'Eduardo Simioni') {
        capability 'Sensor'
        capability 'Presence Sensor'
    }
    preferences {
        input (name: 'timeout', type: 'number', title: 'Timeout', description: 'In milliseconds', defaultValue: '5000', range: '1..*', required: true)
    }
}

#include edu.zigbee-utils
#include edu.hubee-lib

def getEndpoint() {
    return EP_PIR
}

def getEventName() {
    return 'presence'
}

def getEventFormats() {
    return '%s'
}

def getConfigPayload() {
    return "{\"${PRM_TIMEOUT}\":${timeout}}"
}