metadata {
    definition (name: 'Hubee Parent', namespace: 'edu', author: 'Eduardo Simioni') {
        capability 'Sensor'
        capability 'Voltage Measurement'
        capability 'Temperature Measurement'

        attribute 'free.mem', 'integer'
        attribute 'rssi', 'integer'
        attribute 'firmware', 'integer'
        attribute 'software', 'integer'

        command 'rebootXBee'
    }
}

#include edu.hubee-lib
#include edu.zigbee-utils
#include edu.numeric-change-device

import groovy.transform.Field

@Field static final NAME_PREFIX    = 'XB3 '
@Field static final HANDLER_PREFIX = 'Hubee '

def parse(description) {
    def descMap  = parseDescriptionAsMap(description)
    def cluster  = descMap.clusterInt
    def endpoint = descMap.sourceEndpoint
    def command  = descMap.command
    def device   = isChildEndpoint(endpoint) ? getOrCreateChild(endpoint, cluster) : this
    def status   = device.parseStatus(descMap)

    handleCommand(device, endpoint, cluster, command, status)
}

def handleCommand(device, endpoint, cluster, command, status) {
    if (device.traceEnabled()) device.logTrace "Received - endpoint: ${endpoint}, cluster: ${cluster}, command: ${command}, status: ${status}"
    if (device.debugEnabled()) device.logDebug ">> EP ${endpoint} received ${command}: ${status}"
    if (cluster == CL_IGNORE || isProtocolEndpoint(endpoint)) {
        if (device.traceEnabled()) device.logTrace 'Ignored command for ZDO (endpoint 00) or cluster 149'
        return
    }
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
        default:
            device.logWarn "Unknown command: endpoint: ${endpoint}, cluster: ${cluster}, command: ${command}, status: ${status}"
            break
    }
}

def getOrCreateChild(endpoint, cluster) {
    def childDevice = findChildDevice(endpoint)
    return childDevice == null ? createChildDevice(endpoint, cluster) : childDevice
}

def findChildDevice(endpoint) {
    return getChildDevice(getChildNetworkId(endpoint))
}

@groovy.transform.Synchronized
def createChildDevice(endpoint, cluster) {
    def childDevice = findChildDevice(endpoint)
    if (childDevice != null) {
        return childDevice
    }
    def deviceHandlerName = ''
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
        case EP_PIR:
            deviceHandlerName = "${HANDLER_PREFIX}PIR Motion Sensor"
            break
    }
    logInfo "Child creation for endpoint: ${endpoint}, cluster: ${cluster}"
    def deviceName = getNameWithoutPrefix() + ' ' + deviceHandlerName.substring(HANDLER_PREFIX.length(), deviceHandlerName.lastIndexOf(' '))
    logInfo "Creating child '${deviceName}' with network id: " + getChildNetworkId(endpoint)
    return addChildDevice(deviceHandlerName, getChildNetworkId(endpoint), [name: deviceName])
}

def getChildNetworkId(endpoint) {
    return "${device.id}${getChildDniTag()}${endpoint}"
}

def getEndpoint() {
    return EP_XBEE
}

def getEventName() {
    return 'voltage|free.mem|rssi|firmware|temperature|software'
}

def getEventFormats() {
    return '%sV|%s bytes|-%sdBm|%s|%s°C|v%s'
}

def getNameWithPrefix() {
    return (device.displayName.startsWith(NAME_PREFIX) ? device.displayName : NAME_PREFIX + device.displayName).take(20)
}

def getNameWithoutPrefix() {
    return device.displayName.startsWith(NAME_PREFIX) ? device.displayName.substring(NAME_PREFIX.length()) : device.displayName
}

def getDeviceLablel() {}

def rebootXBee() {
    log.warn("${device.displayName}: Rebooting XBee - ATCMD: FR (Force Reboot)")
    def zigbeeCommand = createXBeeATCommand('46 52') // F = 46, R = 52
    if (debugEnabled()) log.debug("${device.displayName}: Sending '${zigbeeCommand}'")
    return zigbeeCommand
}

def createXBeeATCommand(String command) {
    // 00 32 - Fixed, apparently don't have any impact if changed
    // frame-id: 2 bytes API frame ID used in many XBee API calls - Using 00 00 since we don't care about the response
    // sender-ieee-addr: the 64 bit IEEE address (8 bytes, the most significant byte first) - Using the coordinator address
    // 00 00 - Couldn't find an explanation
    // atcmd0: the ASCII code of first character of the AT command (eg 46 or 'F' if command is ATFR)
    // atcmd1: the ASCII code of the second char of the AT command (eg 52 or 'R' if command is ATFR)
    // params: zero, one or more optional parameter bytes - Not using here since RF (Force Reboot) command doesn't take parameters 
    def payload = "00 32 00 00 000D6F00163622D2 00 00 ${command}"
    // he raw [16 bit address] [source endpoint] [destination endpoint] [cluster id] {[payload]} {[profile id]}
    // Example: he raw 0xE700 0xE6 0xE6 0x0021 0013A20041F5B0A3 {00 32 00 0F 00 0D 6F 00 16 36 22 D2 00 00 46 52} {0xC105}'
    return "he raw 0x${device.deviceNetworkId} 0xE6 0xE6 0x0021 ${device.zigbeeId} {${payload}} {0xC105}"
}

def getExtraConfig() {
    return ",\"${PRM_NAME}\":\"${getNameWithPrefix()}\""
}