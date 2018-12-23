const path = require('path')
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin
const { buildDir } = require('../env')

module.exports = new BundleAnalyzerPlugin({
  analyzerMode: 'static',
  reportFilename: path.join(buildDir, 'webpack-bundle-report.html'),
  openAnalyzer: false
})
