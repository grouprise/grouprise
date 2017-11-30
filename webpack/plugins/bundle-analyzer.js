const path = require('path')
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin
const { baseDir } = require('../env')

module.exports = new BundleAnalyzerPlugin({
  analyzerMode: 'static',
  reportFilename: path.join(baseDir, 'build/webpack-bundle-report.html'),
  openAnalyzer: false
})
