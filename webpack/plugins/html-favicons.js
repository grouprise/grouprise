const path = require('path')
const FaviconsWebpackPlugin = require('favicons-webpack-plugin')
const { imgDir, pkg } = require('../env')

module.exports = new FaviconsWebpackPlugin({
  logo: path.join(imgDir, 'logos/logo_small.png'),
  background: '#2a62ac',
  title: pkg.title,
  icons: {
    android: false,
    appleIcon: false,
    appleStartup: false,
    coast: false,
    favicons: true,
    firefox: false,
    opengraph: false,
    twitter: false,
    yandex: false,
    windows: false
  }
})
