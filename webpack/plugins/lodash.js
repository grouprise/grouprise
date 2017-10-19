const LodashModuleReplacementPlugin = require('lodash-webpack-plugin')

module.exports = new LodashModuleReplacementPlugin({
  'shorthands': true,
  'collections': true,
  'paths': true
})
