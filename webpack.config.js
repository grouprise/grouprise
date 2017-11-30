const { nodeEnv } = require('./webpack/env')
const config = require('./webpack/envs/' + nodeEnv)

module.exports = config
