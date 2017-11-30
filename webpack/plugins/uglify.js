const UglifyJSPlugin = require('uglifyjs-webpack-plugin')
const { isDebug } = require('../env')

module.exports = new UglifyJSPlugin({
  sourceMap: !isDebug
})
