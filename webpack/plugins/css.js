const MiniCssExtractPlugin = require('mini-css-extract-plugin')

const miniCssPlugin = new MiniCssExtractPlugin({
  filename: '[contenthash].css'
})

module.exports = miniCssPlugin
