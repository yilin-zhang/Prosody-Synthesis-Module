const OSC = require('osc-js')

const config = { udpClient: { port: 8088 } }
const osc = new OSC({ plugin: new OSC.BridgePlugin(config) })

osc.open() // start a WebSocket server on port 8080
// osc.open({ host: '127.0.0.1', port: 8080 })