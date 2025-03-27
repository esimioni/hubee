library (
    author      : 'Eduardo Simioni',
    namespace   : 'edu',
    name        : 'zigbee-utils',
    category    : 'common',
    description : 'Utility methods'
)

metadata {
    preferences {
        input (name: 'debug', type: 'bool', title: 'Debug logging', description: '', defaultValue: false, required: true)
        input (name: 'trace', type: 'bool', title: 'Trace logging', description: '', defaultValue: false, required: true)
        input (name: 'logStatus', type: 'bool', title: 'Status logging', description: '', defaultValue: true, required: true)
    }
}

def handleEvent(status) {
    def statuses = status.split('\\|')
    def events = getEventName().split('\\|')
    def formats = getEventFormats().split('\\|')
    if (trace) logTrace "Statuses: ${statuses}"
    if (trace) logTrace "Events  : ${events}"
    if (trace) logTrace "Formats : ${formats}"
    statuses.eachWithIndex{ stat, index ->
        def eventMap = [name: events[index], value: stat]
        if (logStatus) logInfo "${eventMap.name} is " + String.format(formats[index], eventMap.value)
        sendEvent(eventMap)
    }
}

def sendZigbeeCommand(endpoint, command, payload, cluster = 1) {
    if (payload.length() > 75) {
        logError 'Zigbee payload over 75 characters cannot be sent'
        return
    }
    if (trace) logTrace "Sending - endpoint: ${endpoint}, cluster: ${cluster}, command: ${command}, payload: ${payload}"
    def actualSender = isChildDevice() ? getParent() : device
    def hexPayload = hubitat.helper.HexUtils.byteArrayToHexString(payload.getBytes())
    def zigbeeCommand = "he cmd 0x${actualSender.deviceNetworkId} 0x${endpoint} 0x${cluster} 0x${command} {${hexPayload}}"
    if (trace) logTrace "Sending '${zigbeeCommand}'"
    sendHubCommand(new hubitat.device.HubAction(zigbeeCommand, hubitat.device.Protocol.ZIGBEE))
}

def isChildDevice() {
    return device.deviceNetworkId.contains(getChildDniTag())
}

def getChildDniTag() {
    return '-EP-'
}

def parseStatus(descMap) {
    if (trace) logTrace "descMap: ${descMap}"
    def status = ''
    for (element in descMap.data) {
        status = status + element
    }
    return zigbee.hex2String(status);
}

def parseDescriptionAsMap(description) {
    return zigbee.parseDescriptionAsMap(description)
}

def debugEnabled() {
    return debug
}

def traceEnabled() {
    return trace
}

def getLogMessage(str) {
    return "${device.displayName}: ${str}"
}

def logTrace(str) {
    log.trace(getLogMessage(str))
}

def logDebug(str) {
    log.debug(getLogMessage(str))
}

def logInfo(str) {
    log.info(getLogMessage(str))
}

def logWarn(str) {
    log.warn(getLogMessage(str))
}

def logError(str) {
    log.error(getLogMessage(str))
}