const { cloneDeep, assign } = require('lodash')
const commonConfig = cloneDeep(require('../presets/common'))

module.exports = assign({}, commonConfig, {
  plugins: [
    require('../plugins/define'),
    require('../plugins/lodash'),
    require('../plugins/loader-options')
  ]
})
