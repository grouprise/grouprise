const path = require('path')
const { baseDir, buildDir, isDebug, jsDir, cssDir, imgDir } = require('../env')
const extractTextPlugin = require('../plugins/extract-text')

const resolveFilename = file => {
  // resolve files in node_modules, in build dir and font files to hash filenames
  if (
    file.indexOf('node_modules/') !== -1 ||
    file.indexOf(buildDir) !== -1 ||
    /\.(ttf|woff|woff2|eot)$/.test(file)) {
    return '[hash].[ext]'
  }

  // any other file should keep the original filename
  return '[path][name].[ext]?[hash]'
}

module.exports = {
  resolve: {
    alias: {
      app: jsDir,
      css: cssDir,
      img: imgDir,
      'vue$': 'vue/dist/vue.runtime.common.js',
      'modernizr$': path.resolve(baseDir, '.modernizrrc')
    }
  },
  module: {
    noParse: [
      /node_modules\/json-schema\/lib\/validate\.js/,
      /moment.js/
    ],
    rules: [
      extractTextPlugin.lessConfig,
      {
        test: /\.vue$/,
        loader: 'vue-loader'
      },
      {
        test: /\.modernizrrc$/,
        use: ['modernizr-loader', 'json-loader']
      },
      {
        loader: 'babel-loader',
        test: /\.jsx?$/,
        include: [jsDir],
        options: {
          plugins: isDebug ? [] : [
            'transform-remove-debugger',
            'transform-remove-console'
          ]
        }
      },
      {
        test: /\.html$/,
        use: {
          loader: 'html-loader',
          options: {
            sourceMap: true,
            minimize: true
          }
        }
      },
      {
        test: /\.(png|jpe?g|gif|ttf|woff|woff2|eot)$/,
        use: [
          {
            loader: 'file-loader',
            options: {
              name: resolveFilename
            }
          }
        ]
      },
      {
        test: /\.svg$/,
        use: [
          {
            loader: 'file-loader',
            options: {
              name: resolveFilename
            }
          },
          {
            loader: 'svgo-loader',
            options: {
              sourceMap: true,
              plugins: [
                { removeUselessDefs: false },
                { cleanupIDs: false }
              ]
            }
          }
        ]
      }
    ]
  },
  node: {
    fs: 'empty',
    net: 'empty',
    tls: 'empty'
  }
}
