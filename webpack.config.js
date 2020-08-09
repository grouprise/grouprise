const fs = require('fs')
const path = require('path')

const _ = require('lodash')
const webpack = require('webpack')
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const CleanWebpackPlugin = require('clean-webpack-plugin').CleanWebpackPlugin
const HtmlWebpackHarddiskPlugin = require('html-webpack-harddisk-plugin')
const LodashModuleReplacementPlugin = require('lodash-webpack-plugin')
const VueLoaderPlugin = require('vue-loader/lib/plugin')

const env = _.has(process.env, 'NODE_ENV') ? process.env.NODE_ENV : 'development'
const isDebug = env !== 'production'
const banner = require('./res/templates/banner.txt.js')
const baseDir = __dirname
const buildDir = process.env.DIR_BUILD || path.join(baseDir, 'build')
const reportsDir = path.join(buildDir, 'reports')

const postCss = {
  loader: 'postcss-loader',
  options: {
    sourceMap: true,
    ident: 'postcss',
    plugins: () => [
      require('autoprefixer'),
      require('cssnano')(),
      require('postcss-banner')({ banner }),
      require('postcss-preset-env')()
    ]
  }
}

module.exports = {
  mode: env,
  context: path.join(__dirname, 'res', 'js'),
  devtool: isDebug ? 'eval' : 'source-map',
  entry: './index.js',
  output: {
    publicPath: `${isDebug ? 'http://localhost:8080' : ''}/stadt/static/core/base/`,
    path: path.join(__dirname, 'build', 'static'),
    filename: '[name].[hash].js'
  },
  resolve: {
    alias: {
      app: path.resolve(__dirname, 'res', 'js'),
      vue$: 'vue/dist/vue.common.js'
    }
  },
  devServer: {
    contentBase: './dist',
    hot: true,
    overlay: true,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
      'Access-Control-Allow-Headers': 'X-Requested-With, Content-Type, Authorization'
    }
  },
  module: {
    noParse: [
      /node_modules\/json-schema\/lib\/validate\.js/
    ],
    rules: [
      {
        test: /\.vue$/,
        loader: 'vue-loader'
      },
      {
        loader: 'babel-loader',
        test: /\.jsx?$/,
        include: [
          path.resolve(__dirname, 'res/js')
        ],
        options: {
          plugins: isDebug ? [] : [
            'transform-remove-debugger',
            ['transform-remove-console', { exclude: ['error', 'warn'] }]
          ]
        }
      },
      {
        test: /\.css$/,
        use: [
          isDebug ? 'vue-style-loader' : MiniCssExtractPlugin.loader,
          {
            loader: 'css-loader',
            options: {
              sourceMap: true
            }
          },
          postCss
        ]
      },
      {
        test: /\.less$/,
        use: [
          isDebug ? 'vue-style-loader' : MiniCssExtractPlugin.loader,
          {
            loader: 'css-loader',
            options: {
              sourceMap: true
            }
          },
          postCss,
          {
            loader: 'less-loader',
            options: {
              sourceMap: true,
              lessOptions: {
                strictMath: true,
                strictUnits: true,
                noIeCompat: true,
                outputSourceFiles: true,
                sourceMapFileInline: true,
                globalVars: {
                  'build-root': `'${buildDir}'`
                }
              }
            }
          }
        ]
      },
      {
        test: /\.(png|jpe?g|gif|webp|ttf|otf|woff2?|eot)$/,
        use: [
          {
            loader: 'file-loader',
            options: {}
          }
        ]
      },
      {
        test: /\.html$/,
        use: {
          loader: 'html-loader',
          options: {
            sourceMap: true
          }
        }
      },
      {
        test: /\.svg$/,
        use: [
          {
            loader: 'file-loader'
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
  plugins: [
    new CleanWebpackPlugin(),
    new webpack.BannerPlugin(banner),
    new BundleAnalyzerPlugin({
      analyzerMode: 'static',
      openAnalyzer: false,
      generateStatsFile: true,
      reportFilename: path.join(reportsDir, 'webpack-report.html'),
      statsFilename: path.join(reportsDir, 'webpack-report-stats.json')
    }),
    new VueLoaderPlugin(),
    new MiniCssExtractPlugin({
      filename: '[name].[hash].css',
      chunkFilename: isDebug ? '[id].[hash].css' : '[id].css'
    }),
    new LodashModuleReplacementPlugin({
      collections: true,
      paths: true,
      shorthands: true
    }),
    new webpack.ContextReplacementPlugin(/moment[/\\]locale$/, /de/),
    new webpack.LoaderOptionsPlugin({
      minimize: !isDebug,
      debug: isDebug
    }),
    new HtmlWebpackPlugin({
      filename: path.join(__dirname, 'grouprise', 'core', 'templates', 'core', '_assets.html'),
      scriptLoading: 'defer',
      inject: false,
      alwaysWriteToDisk: true,
      templateContent ({ htmlWebpackPlugin }) {
        const tags = [].concat(htmlWebpackPlugin.tags.headTags, htmlWebpackPlugin.tags.bodyTags)
        return tags.join('\n')
      }
    }),
    new HtmlWebpackHarddiskPlugin()
  ]
}
