const { nodeEnv } = require('./webpack/env')
const config = require('./webpack/envs/' + nodeEnv)
process.traceDeprecation = true
module.exports = config
