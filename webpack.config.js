const path = require('path')
const fs = require('fs')
const webpack = require('webpack')
const LodashModuleReplacementPlugin = require('lodash-webpack-plugin')
const _ = require('lodash')

const banner = fs.readFileSync('res/templates/banner.txt', 'utf-8')
const env = _.has(process.env, 'NODE_ENV') ? process.env.NODE_ENV : 'development'
const isDebug = env !== 'production'

module.exports = {
  context: path.join(__dirname, 'res/js'),
  devtool: isDebug ? '#eval' : '#source-map',
  entry: {
    app: './index.js',
    snake: './snake.js'
  },
  output: {
    publicPath: '/static/stadt/js/',
    path: path.join(__dirname, 'build/static/js/'),
    filename: '[name].js'
  },
  resolve: {
    alias: {
      app: path.resolve(__dirname, 'res/js'),
      'vue$': 'vue/dist/vue.runtime.common.js'
    }
  },
  module: {
    noParse: /node_modules\/json-schema\/lib\/validate\.js/,
    rules: [
      {
        test: /\.vue$/,
        loader: 'vue-loader',
      },
      {
        test: /\.jsx?$/,
        include: [
          path.resolve(__dirname, 'res/js')
        ],
        loader: 'babel-loader'
      }
    ]
  },
  plugins: [
    new LodashModuleReplacementPlugin({
      'collections': true,
      'paths': true
    }),
    new webpack.BannerPlugin(banner),
    new webpack.ContextReplacementPlugin(/moment[/\\]locale$/, /de/),
    new webpack.optimize.UglifyJsPlugin({
      sourceMap: !isDebug,
      compress: {
        warnings: !isDebug
      }
    }),
    new webpack.LoaderOptionsPlugin({
      minimize: !isDebug,
      debug: isDebug
    }),
    new webpack.DefinePlugin({
      'process.env': {
        NODE_ENV: JSON.stringify(env)
      }
    })
  ]
}
