metadata {
    definition (name: 'Hubee Presence Sensor', namespace: 'edu', author: 'Eduardo Simioni') {
        capability 'Sensor'
        capability 'Presence Sensor'
    }
    preferences {
        input (name: 'timeout', type: 'number', title: 'Timeout', description: 'In milliseconds', defaultValue: '5000', range: '1..500000000', required: true)
        input (name: 'movementOnly', type: 'bool', title: 'Movement Only', description: 'Disable occupancy detection', defaultValue: False, required: true)
        input (name: 'usePIR', type: 'bool', title: 'Use PIR', description: 'Combines with a PIR sensor to avoid undue triggering', defaultValue: False, required: true)
        input (name: 'rmax', type: 'decimal', title: 'Range', description: 'Max detection distance in meters, one decimal place can be used', defaultValue: '6.0', range: '0.1..12', required: true)
        input (name: 'mth1', type: 'number', title: 'mth1', description: 'Sensitivity within 2.8 meters (lower = more sensitive)', defaultValue: '60', range: '0..*', required: true)
        input (name: 'mth2', type: 'number', title: 'mth2', description: 'Sensitivity in 2.8-8 meters range (lower = more sensitive)', defaultValue: '30', range: '0..*', required: true)
        input (name: 'mth3', type: 'number', title: 'mth3', description: 'Sensitivity beyond 8 meters (lower = more sensitive)', defaultValue: '20', range: '0..*', required: true)
    }
}

#include edu.zigbee-utils
#include edu.hubee-lib

def getEndpoint() {
    return EP_PRESENCE
}

// TODO change to 'motion' and 'active'/'inactive'
def getEventName() {
    return 'presence'
}

def getEventFormats() {
    return '%s'
}

def getConfigPayload() {
    return "{\"${PRM_TIMEOUT}\":${timeout}," +
            "\"${PRM_MOV_ONLY}\":${movementOnly ? 1 : 0}," +
            "\"${PRM_PIR}\":${usePIR ? 1 : 0}," +
            "\"${PRM_RADAR}\":\"rmax=${rmax};mth1=${mth1};mth2=${mth2};mth3=${mth3}\"}"
}