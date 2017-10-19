const { resDir, isDebug, staticDir } = require('../env')

module.exports = {
  app: {
    context: resDir,
    devtool: isDebug ? '#eval' : '#source-map',
    entry: {
      'app': './js/index.js'
    },
    output: {
      publicPath: '/stadt/static/stadt/',
      path: staticDir,
      filename: '[hash].js',
      chunkFilename: '[chunkhash].js'
    }
  },
  snake: {
    context: resDir,
    devtool: isDebug ? '#eval' : '#source-map',
    entry: {
      'snake': './js/snake.js'
    },
    output: {
      publicPath: '/stadt/static/stadt/',
      path: staticDir,
      filename: '[name].js'
    }
  }
}
