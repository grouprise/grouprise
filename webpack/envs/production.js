const { cloneDeep, assign } = require('lodash')
const commonConfig = cloneDeep(require('../presets/common'))
const { app, snake } = cloneDeep(require('../presets/files'))

module.exports = [
  assign({}, commonConfig, app, {
    plugins: [
      require('../plugins/html'),
      require('../plugins/html-favicons'),
      require('../plugins/html-pwa'),
      require('../plugins/define'),
      require('../plugins/lodash'),
      require('../plugins/loader-options'),
      require('../plugins/extract-text'),
      require('../plugins/common-chunks'),
      require('../plugins/uglify'),
      require('../plugins/bundle-analyzer'),
      require('../plugins/banner')
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
