library (
    author      : "Eduardo Simioni",
    namespace   : "edu",
    name        : "numeric-change-device",
    category    : "common",
    description : "Common numeric change device code"
)

metadata {
    preferences {
        input (name: "offset", type: "decimal", title: "Value offset", description: "", defaultValue: "0", range: "0..*", required: true)
        input (name: "minInterval", type: "number", title: "Minimum report interval", description: "In seconds", defaultValue: "1", range: "1..*", required: true)
        input (name: "maxInterval", type: "number", title: "Maximum report interval", description: "In seconds", defaultValue: "3600", range: "0..*", required: true)
        input (name: "amount", type: "decimal", title: "Fixed or % amount change to trigger report", description: "", defaultValue: "0.1", range: "0..*", required: true)
        input (name: "fixed", type: "bool", title: "Enabled = fixed, disabled = %", description: "", defaultValue: true, required: true)
    }
}

def getConfigPayload() {
    return "{\"${PRM_OFFSET}\":${offset}," +
            "\"${PRM_MIN_INTERVAL}\":${minInterval}," +
            "\"${PRM_MAX_INTERVAL}\":${maxInterval}," +
            "\"${PRM_AMOUNT}\":${amount}," +
            "\"${PRM_FIXED}\":${fixed}" +
            "${getExtraConfig()}}"
}