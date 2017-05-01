'use strict'

const fs = require('fs')
const banner = fs.readFileSync('res/templates/banner.txt', 'utf-8')

module.exports = {
  plugins: [
    require('autoprefixer')({
      browsers: ['last 2 versions', 'ie 11', '> 5%']
    }),
    require('postcss-banner')({
      banner: banner
    }),
    require('csswring')
  ]
}
