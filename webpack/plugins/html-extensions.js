const HtmlWebpackPlugin = require('html-webpack-plugin')

class GroupriseHTMLExtensionsPlugin {
  apply (compiler) {
    compiler.hooks.compilation.tap('GroupriseHTMLExtensionsPlugin', (compilation) => {
      HtmlWebpackPlugin.getHooks(compilation).beforeEmit.tapAsync(
        'GroupriseHTMLExtensionsPlugin',
        (data, callback) => {
          data.html = data.html
            .replace(/<head>/, '')
            .replace(/<\/head>/, '')
            // the `defer` is important here because it forces the scripts to be
            // executed once all html is loaded instead of blocking the parser
            // and executing right away. this makes it possible to initialize all
            // js components without any kind of dom-content-loader logic.
            .replace(/src="([^"]+\.js)">/g, 'defer src="$1">')
          callback(null, data)
        }
      )
    })
  }
}

module.exports = new GroupriseHTMLExtensionsPlugin()
