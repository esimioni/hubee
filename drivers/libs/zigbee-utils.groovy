library (
    author      : "Eduardo Simioni",
    namespace   : "edu",
    name        : "zigbee-utils",
    category    : "common",
    description : "Utility methods"
)

metadata {
    preferences {
        input (name: "debug", type: "bool", title: "Debug logging", description: "", defaultValue: false, required: true)
        input (name: "trace", type: "bool", title: "Trace logging", description: "", defaultValue: false, required: true)
        input (name: "logStatus", type: "bool", title: "Status logging", description: "", defaultValue: true, required: true)
    }
}

def handleEvent(status) {
    def eventMap = [name: getEventName(), value: status]
    if (logStatus) logInfo "Status: ${device.displayName}: ${eventMap.value}"
    sendEvent(eventMap)
}

def sendZigbeeCommand(endpoint, command, payload, cluster = 1) {
    if (payload.length() > 77) {
        logError "Zigbee payload over 77 characters cannot be sent"
        return
    }
    if (trace) logTrace "Sending - endpoint: ${endpoint}, cluster: ${cluster}, command: ${command}, payload: ${payload}"
    actualSender = isChildDevice() ? getParent() : device
    def hexPayload = hubitat.helper.HexUtils.byteArrayToHexString(payload.getBytes())
    def zigbeeCommand = "he cmd 0x${actualSender.deviceNetworkId} 0x${endpoint} 0x${cluster} 0x${command} {${hexPayload}}"
    if (trace) logTrace "Sending '${zigbeeCommand}'"
    sendHubCommand(new hubitat.device.HubAction(zigbeeCommand, hubitat.device.Protocol.ZIGBEE))
}

def isChildDevice() {
    return device.deviceNetworkId.contains("-HI-")
}

def parseStatus(descMap) {
    if (trace) logTrace "descMap: ${descMap}"
    def status = ""
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

def logTrace(str) {
    log.trace(str)
}

def logDebug(str) {
    log.debug(str)
}

def logInfo(str) {
    log.info(str)
}

def logWarn(str) {
    log.warn(str)
}

def logError(str) {
    log.error(str)
}