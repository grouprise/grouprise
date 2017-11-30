const webpack = require('webpack')

module.exports = new webpack.optimize.CommonsChunkPlugin({
  name: 'vendor',
  filename: '[name].[hash].js',
  minChunks: function (module, count) {
    if (module.resource && (/^.*\.(css|scss|less)$/).test(module.resource)) {
      return false
    }

    return (module.context && module.context.indexOf('node_modules') !== -1) || count >= 2
  }
})
