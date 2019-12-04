const { cloneDeep, assign } = require('lodash')
const commonConfig = cloneDeep(require('../presets/common'))
const { app, snake } = cloneDeep(require('../presets/files'))

module.exports = [
  assign({}, commonConfig, app, {
    plugins: [
      require('../plugins/html'),
      require('../plugins/html-favicons'),
      require('../plugins/html-pwa'),
      require('../plugins/html-extensions'),
      require('../plugins/define'),
      require('../plugins/lodash'),
      require('../plugins/loader-options'),
      require('../plugins/css'),
      require('../plugins/uglify'),
      require('../plugins/bundle-analyzer'),
      require('../plugins/banner'),
      require('../plugins/vue')
    ]
  }),
  assign({}, commonConfig, snake, {
    plugins: [
      require('../plugins/define'),
      require('../plugins/lodash'),
      require('../plugins/loader-options'),
      require('../plugins/uglify'),
      require('../plugins/banner')
    ]
  })
]
