import './setup'

import { $$, component, mapCall } from 'luett'
import closest from 'closest'

import date from './transforms/date'
import editor from './transforms/editor'
import time from './transforms/time'
import userContent from './transforms/user-content'
import gallery from './transforms/gallery'
import transformIcon from './transforms/transformicons'
import input from './transforms/input'
import snake from './transforms/snake'
import openable from './transforms/openable'
import clipboard from './transforms/clipboard'
import browserWarning from './transforms/browser-warning'
import carousel from './transforms/carousel'
import conversation from './transforms/conversation'
import keysubmit from './transforms/keysubmit'

function init (searchIn = document) {
  const opts = { root: searchIn }

  // initialize components on load
  component('date', date, opts)
  component('editor', editor, opts)
  component('time', time, opts)
  component('user-content', userContent, opts)
  component('gallery', gallery, opts)
  component('snake', snake, opts)
  component('openable', openable, opts)
  component('clipboard', clipboard, opts)
  component('browser-warning', browserWarning, opts)
  component('carousel', carousel, opts)
  component('tcon', transformIcon, opts)
  component('conversation', conversation, Object.assign({}, opts, { conf: { init } }))
  component('keysubmit', keysubmit, opts)

  // initialize components not based on component interface
  mapCall($$('input, textarea'), (el) => input(el, { target: closest(el, '.form-group') }))
}

init()
