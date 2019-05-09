const path = require('path')
const WebpackPwaManifest = require('webpack-pwa-manifest')
const { pkg, imgDir } = require('../env')

module.exports = new WebpackPwaManifest({
  name: pkg.name,
  short_name: pkg.name,
  description: pkg.description,
  version: pkg.version,
  start_url: '/',
  display: 'standalone',
  background_color: '#ffffff',
  theme_color: '#2a62ac',
  orientation: 'portrait',
  icons: [
    {
      src: path.join(imgDir, 'logos/logo_large.png'),
      sizes: [128, 144, 192, 256, 384, 512],
      ios: true
    },
    {
      src: path.join(imgDir, 'logos/logo_small.png'),
      sizes: [32, 48, 64, 72, 96],
      ios: true
    }
  ],
  ios: {
    'apple-mobile-web-app-title': 'grouprise',
    'apple-mobile-web-app-status-bar-style': 'black'
  }
})
