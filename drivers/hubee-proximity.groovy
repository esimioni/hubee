metadata {
    definition (name: 'Hubee Proximity Sensor', namespace: 'edu', author: 'Eduardo Simioni') {
        capability 'Sensor'
        capability 'Presence Sensor'
    }
    preferences {
        input (name: 'timeout', type: 'number', title: 'Timeout', description: 'In milliseconds', defaultValue: '5000', range: '1..*', required: true)
        input (name: 'minTriggerDistance', type: 'number', title: 'Minimum trigger distance', description: 'In millimeters', defaultValue: '30', range: '1..*', required: true)
        input (name: 'maxTriggerDistance', type: 'number', title: 'Maximum trigger distance', description: 'In millimeters', defaultValue: '500', range: '1..*', required: true)
    }
}

#include edu.zigbee-utils
#include edu.hubee-lib

def getEndpoint() {
    return EP_PROXIMITY
}

def getEventName() {
    return 'presence'
}

def getEventFormats() {
    return '%s'
}

def getConfigPayload() {
    return "{\"${PRM_TIMEOUT}\":${timeout},\"${PRM_MIN_DISTANCE}\":${minTriggerDistance},\"${PRM_MAX_DISTANCE}\":${maxTriggerDistance}}"
}