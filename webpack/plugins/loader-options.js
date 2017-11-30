const webpack = require('webpack')
const { isDebug } = require('../env')

module.exports = new webpack.LoaderOptionsPlugin({
  minimize: !isDebug,
  debug: isDebug
})
