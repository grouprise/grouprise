const webpack = require('webpack')
const banner = require('../../res/templates/banner.txt.js')

module.exports = new webpack.BannerPlugin(banner)
