metadata {
    definition (name: "Hubee Parent", namespace: "edu", author: "Eduardo Simioni") {
        capability "Sensor"
        capability "Voltage Measurement"

        command "rebootXBee"
        command "enableBluetooth"
    }
}

#include edu.numeric-change-device
#include edu.zigbee-utils
#include edu.hubee-lib

import groovy.transform.Field

@Field static final CMD_REBOOT     = 1
@Field static final CMD_BLE_ENABLE = 3
@Field static final CMD_REFRESH    = 4

@Field static final NAME_PREFIX    = 'XB3 '
@Field static final HANDLER_PREFIX = 'Hubee '

def parse(description) {
    def descMap  = parseDescriptionAsMap(description)
    def cluster  = descMap.clusterInt
    def endpoint = descMap.sourceEndpoint
    def command  = descMap.command
    def isChild  = endpoint != EP_XBEE && endpoint != EP_DEFAULT
    def device   = isChild ? getOrCreateChild(endpoint, cluster) : this
    def status   = device.parseStatus(descMap)

    handleCommand(device, endpoint, cluster, command, status)
}

def handleCommand(device, endpoint, cluster, command, status) {
    if (device.traceEnabled()) device.logTrace "Received - endpoint: ${endpoint}, cluster: ${cluster}, command: ${command}, status: ${status}"
    if (device.debugEnabled()) device.logDebug ">> EP ${endpoint} received ${command}: ${status}"
    switch(command) {
        case CMD_STATUS:
            device.handleEvent(status)
            break
        case CMD_STARTED:
            device.logInfo "${status}"
            break
        case CMD_CONFIG:
            device.logInfo "Device request: ${status}"
            device.configure()
            break
        case CMD_REPLY:
            device.logInfo "Device replied: ${status}"
            break
        case CMD_INFO:
            device.logInfo "Device info: ${status}"
            break
        case CMD_WARN:
            device.logWarn "Device warn: ${status}"
            break
        case CMD_ERROR:
            device.logError "Device error: ${status}"
            break
    }
}

def getOrCreateChild(endpoint, cluster) {
    if (cluster == CL_IGNORE) {
        return
    }
    def childDevice = findChildDevice(endpoint, cluster)
    return childDevice == null ? createChildDevice(endpoint, cluster) : childDevice
}

def findChildDevice(endpoint, cluster) {
    return getChildDevice(getChildNetworkId(endpoint))
}

@groovy.transform.Synchronized
def createChildDevice(endpoint, cluster) {
    def childDevice = findChildDevice(endpoint, cluster)
    if (childDevice != null) {
        return childDevice
    }
    def deviceHandlerName = ""
    switch(endpoint) {
        case EP_CONTACT:
            deviceHandlerName = "${HANDLER_PREFIX}Contact Sensor" 
            break
        case EP_PRESENCE:
            deviceHandlerName = "${HANDLER_PREFIX}Presence Sensor"
            break
        case EP_TEMPERATURE: 
            deviceHandlerName = "${HANDLER_PREFIX}Temperature Sensor" 
            break
        case EP_HUMIDITY:
            deviceHandlerName = "${HANDLER_PREFIX}Humidity Sensor" 
            break
        case EP_PRESSURE:
            deviceHandlerName = "${HANDLER_PREFIX}Pressure Sensor" 
            break
        case EP_AIR_QUALITY:
            deviceHandlerName = "${HANDLER_PREFIX}Air Quality Sensor" 
            break
        case EP_ILLUMINANCE:
            deviceHandlerName = "${HANDLER_PREFIX}Lux Sensor" 
            break
        case EP_PROXIMITY:
            deviceHandlerName = "${HANDLER_PREFIX}Proximity Sensor" 
            break
    }
    def deviceName = getNameWithoutPrefix() + ' ' + deviceHandlerName.substring(HANDLER_PREFIX.length(), deviceHandlerName.lastIndexOf(' '))
    logInfo "Creating child '${deviceName}' with network id: " + getChildNetworkId(endpoint)
    return addChildDevice(deviceHandlerName, getChildNetworkId(endpoint), [name: deviceName])
}

def getChildNetworkId(endpoint) {
    return "${device.id}-${device.deviceNetworkId}-HI-${endpoint}"
}

def getEndpoint() {
    return EP_XBEE
}

def getEventName() {
    return "voltage"
}

def getNameWithPrefix() {
    return (device.getLabel().startsWith(NAME_PREFIX) ? device.getLabel() : NAME_PREFIX + device.getLabel()).take(20)
}

def getNameWithoutPrefix() {
    return device.getLabel().startsWith(NAME_PREFIX) ? device.getLabel().substring(NAME_PREFIX.length()) : device.getLabel()
}

def rebootXBee() {
    sendZigbeeCommand(CMD_REBOOT, "reboot")
}

def enableBluetooth() {
    sendZigbeeCommand(CMD_BLE_ENABLE, "enable bluetooth")
}

def getExtraConfig() {
    return ",\"${PRM_NAME}\":\"${getNameWithPrefix()}\""
}