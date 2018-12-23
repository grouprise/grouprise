const path = require('path')
const { has } = require('lodash')

const buildEnv = has(process.env, 'BUILD_ENV') ? process.env.BUILD_ENV : 'development'
const nodeEnv = has(process.env, 'NODE_ENV') ? process.env.NODE_ENV : 'development'
const isDebug = nodeEnv !== 'production'

const baseDir = path.join(__dirname, '..')
const buildDir = process.env.DIR_BUILD || path.join(baseDir, 'build')
const publicDir = path.join(buildDir, 'static')
const staticDir = path.join(publicDir, '')
const resDir = path.join(baseDir, 'res')
const templateDir = path.join(baseDir, 'res/templates')
const jsDir = path.join(baseDir, 'res/js')
const imgDir = path.join(baseDir, 'res/img')
const cssDir = path.join(baseDir, 'res/css')
const fontsDir = path.join(baseDir, 'res/fonts')
const pkg = require('../package.json')

module.exports = {
  baseDir,
  publicDir,
  staticDir,
  templateDir,
  resDir,
  jsDir,
  imgDir,
  cssDir,
  fontsDir,
  buildEnv,
  buildDir,
  nodeEnv,
  isDebug,
  pkg
}
