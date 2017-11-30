function HTMLExtensionsPlugin () {}
HTMLExtensionsPlugin.prototype.apply = function (compiler) {
  compiler.plugin('compilation', function (compilation) {
    compilation.plugin('html-webpack-plugin-after-html-processing', function (htmlPluginData, callback) {
      htmlPluginData.html = htmlPluginData.html
        .replace(/<head>/, '')
        .replace(/<\/head>/, '')
        .replace(/<script type="text\/javascript"/g, '<script defer')
        // wtf?
        .replace('<script type="text/javascript" src="undefined"></script>', '')
      callback(null, htmlPluginData)
    })
  })
}

module.exports = new HTMLExtensionsPlugin()
