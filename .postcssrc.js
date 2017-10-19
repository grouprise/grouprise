const { isDebug } = require('./webpack/env')

module.exports = ({ file, options }) => {
  return {
    plugins: {
      'autoprefixer': isDebug ? false : options.autoprefixer || {},
      'cssnano': isDebug ? false : options.cssnano || {}
    }
  }
}
