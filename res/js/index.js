import './setup'

import { $$, component, mapCall } from 'luett'
import closest from 'closest'

import PubSub from './util/pubsub'

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
import select from './transforms/select'
import publish from './transforms/publish'
import eventTime from './transforms/event-time'
import dismissible from './transforms/dismissible'
import autosize from './transforms/autosize'

function init (searchIn = document) {
  const bus = PubSub()
  const opts = { root: searchIn, conf: { bus } }

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
  component('select', select, opts)
  component('publish', publish, opts)
  component('event-time', eventTime, opts)
  component('dismissible', dismissible, opts)
  component('autosize', autosize, opts)

  // initialize components not based on component interface
  mapCall($$('input, select, textarea'), (el) => input(el, { target: closest(el, '.form-group') }))
}

init()
