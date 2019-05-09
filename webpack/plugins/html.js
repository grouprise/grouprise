const path = require('path')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const { baseDir, templateDir } = require('../env')

module.exports = new HtmlWebpackPlugin({
  filename: path.join(baseDir, 'grouprise/core/templates/core/_assets.html'),
  template: path.join(templateDir, 'index.html')
})
