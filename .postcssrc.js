const { isDebug } = require('./webpack/env')

module.exports = ({ file, options }) => {
  return {
    plugins: {
      'autoprefixer': isDebug ? false : options.autoprefixer || {},
      'postcss-custom-properties': isDebug ? false : Object.assign({}, {
        preserve: true
      })
    }
  }
}
