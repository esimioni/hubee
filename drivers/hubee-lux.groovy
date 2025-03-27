metadata {
    definition (name: 'Hubee Lux Sensor', namespace: 'edu', author: 'Eduardo Simioni') {
        capability 'Sensor'
        capability 'Illuminance Measurement'
    }
    preferences {
        input (name: 'integrationTime', type: 'enum', title: 'Integration Time', description: '', defaultValue: 100, required: true,
               options: [[100:'100ms'],[200:'200ms'],[400:'400ms'],[800:'800ms']])
        input (name: 'gain', type: 'enum', title: 'Gain', description: '', defaultValue: 1, required: true,
               options: [[0.125:'Low'],[0.25:'Med'],[1:'High'],[2:'Max']])
    }
}

#include edu.numeric-change-device
#include edu.zigbee-utils
#include edu.hubee-lib

def getEndpoint() {
    return EP_ILLUMINANCE
}

def getEventName() {
    return 'illuminance'
}

def getEventFormats() {
    return '%slx'
}

def getExtraConfig() {
    return ",\"${PRM_INTEG_TIME}\":${integrationTime},\"${PRM_GAIN}\":${gain}"
}