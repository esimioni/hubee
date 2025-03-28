library (
    author      : "Eduardo Simioni",
    namespace   : "edu",
    name        : "hubee-lib",
    category    : "common",
    description : "Hubee shared code"
)

// Depends on: edu.zigbee-utils

import groovy.transform.Field

/** ENDPOINTS **/
@Field static final EP_DEFAULT       = 'E8'
@Field static final EP_XBEE          = '01'
@Field static final EP_PRESENCE      = '02'
@Field static final EP_CONTACT       = '03'
@Field static final EP_TEMPERATURE   = '04'
@Field static final EP_HUMIDITY      = '05'
@Field static final EP_PRESSURE      = '06'
@Field static final EP_AIR_QUALITY   = '07'
@Field static final EP_ILLUMINANCE   = '08'
@Field static final EP_PROXIMITY     = '09'
@Field static final EP_PIR           = '0A'

// Ugly, but I couldn't find a way to reference the static endpoint variables above
@Field static final Set<String> CHILD_ENDPOINTS = ['02', '03', '04', '05', '06', '07', '08', '09', '0A']
@Field static final Set<String> KNOWN_ENDPOINTS = ['01', '02', '03', '04', '05', '06', '07', '08', '09']

/** CLUSTERS **/
@Field static final CL_IGNORE        = 149

/** COMMANDS **/
@Field static final CMD_STATUS       = '01'
@Field static final CMD_CONFIG       = '02'
@Field static final CMD_STARTED      = '03'
@Field static final CMD_REPLY        = '04'
@Field static final CMD_UNKNOWN      = '88'
@Field static final CMD_INFO         = '97'
@Field static final CMD_WARN         = '98'
@Field static final CMD_ERROR        = '99'

@Field static final OUT_CMD_CONFIG   = 2

/** CONFIGURATION PARAMETERS **/
@Field static final PRM_PIR          = 'PI'
@Field static final PRM_NAME         = 'NA'
@Field static final PRM_GAIN         = 'GA'
@Field static final PRM_FIXED        = 'FI'
@Field static final PRM_SCALE        = 'SC'
@Field static final PRM_RADAR        = 'RA'
@Field static final PRM_OFFSET       = 'OF'
@Field static final PRM_AMOUNT       = 'AM'
@Field static final PRM_TIMEOUT      = 'TO'
@Field static final PRM_MOV_ONLY     = 'MO'
@Field static final PRM_INTEG_TIME   = 'IT'
@Field static final PRM_OPEN_STATE   = 'OS'
@Field static final PRM_MAX_DISTANCE = 'MA'
@Field static final PRM_MIN_DISTANCE = 'MI'
@Field static final PRM_MAX_INTERVAL = 'MA'
@Field static final PRM_MIN_INTERVAL = 'MI'

def sendZigbeeCommand(command, payload) {
    logInfo "<< EP ${getEndpoint()} sending  ${command}: ${payload}"
    sendZigbeeCommand(getEndpoint(), command, payload)
}

def sendZigbeeConfigure(payload) {
    sendZigbeeCommand(OUT_CMD_CONFIG, payload)
}

def isChildEndpoint(endpoint) {
    return CHILD_ENDPOINTS.contains(endpoint)
}

def isProtocolEndpoint(endpoint) {
    return endpoint == '00' || endpoint == '255'
}

def configure() {
    logInfo 'Configure...'
    sendZigbeeConfigure(getConfigPayload())
}

def updated() {
    configure()
}