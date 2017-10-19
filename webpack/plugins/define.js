const webpack = require('webpack')
const { nodeEnv } = require('../env')

module.exports = new webpack.DefinePlugin({
  'process.env': {
    NODE_ENV: JSON.stringify(nodeEnv)
  }
})
