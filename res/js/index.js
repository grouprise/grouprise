import './setup'

import { $$, component } from 'luett'
import { defaultsDeep } from 'lodash'
import closest from 'closest'

import PubSub from './util/pubsub'

import date from './transforms/date'
import editor from './transforms/editor'
import time from './transforms/time'
import userContent from './transforms/user-content'
import gallery from './transforms/gallery'
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
import cite from './transforms/cite'
import grouplink from './transforms/grouplink'
import quote from './transforms/quote'

function init (searchIn = document) {
  const bus = PubSub()
  const opts = { root: searchIn, conf: { bus, init } }

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
  component('conversation', conversation, opts)
  component('keysubmit', keysubmit, opts)
  component('select', select, opts)
  component('publish', publish, opts)
  component('event-time', eventTime, opts)
  component('dismissible', dismissible, opts)
  component('autosize', autosize, opts)
  component('cite', cite, opts)
  component('grouplink', grouplink, opts)

  // initialize components not based on component interface
  component($$('input, select, textarea'), input, defaultsDeep({
    conf: { target: el => closest(el, '.form-group') }
  }, opts))
  component($$('blockquote'), quote, opts)
}

init()
