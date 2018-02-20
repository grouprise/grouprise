import '../css/app.less'
import './files'
import './config'
import './setup'

import { $$, component } from 'luett'
import { defaultsDeep } from 'lodash'
import closest from 'closest'

import PubSub from './util/pubsub'
import HistoryStateDispatcher from './util/history'

import date from './transforms/date'
import editor from './transforms/editor'
import calendar from './transforms/calendar'
import time from './transforms/time'
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
import masonry from './transforms/masonry'
import galleryEditor from './transforms/gallery-editor'
import imagePicker from './transforms/image-picker'
import poll from './transforms/poll'
import pollEditor from './transforms/poll-editor'
import groupSearch from './transforms/group-search'
import menu from './transforms/menu'
import dock from './transforms/dock'
import contentOrder from './transforms/content-order'

__webpack_nonce__ = 'value'  // eslint-disable-line

const bus = PubSub()
const history = HistoryStateDispatcher()

function init (searchIn = document) {
  const opts = { root: searchIn, conf: { bus, init, history } }

  // initialize components on load
  component('masonry', masonry, opts)
  component('date', date, opts)
  component('menu', menu, opts)
  component('dock', dock, opts)
  component('editor', editor, opts)
  component('time', time, opts)
  component('calendar', calendar, opts)
  component('gallery', gallery, opts)
  component('gallery-editor', galleryEditor, opts)
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
  component('image-picker', imagePicker, opts)
  component('group-search', groupSearch, opts)
  component('poll', poll, opts)
  component('poll-editor', pollEditor, opts)
  component('content-order', contentOrder, opts)

  // initialize components not based on component interface
  component($$('input:not(.vue-input), select, textarea'), input, defaultsDeep({
    conf: { target: el => closest(el, '.form-group') || el }
  }, opts))
  component($$('blockquote').filter(b => !closest(b, 'blockquote')), quote, opts)

  // register popstate handler
  history.mount()
}

init()
