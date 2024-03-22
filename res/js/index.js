import '../css/app.less'
import './config'
import './setup'

import { $$, component } from 'luett'
import { defaultsDeep } from 'lodash'
import closest from 'closest'
import { asyncComponent } from './util/dom'

import PubSub from './util/pubsub'
import HistoryStateDispatcher from './util/history'

import time from './transforms/time'

__webpack_nonce__ = 'value'  // eslint-disable-line

const bus = PubSub()
const history = HistoryStateDispatcher()

function init (searchIn = document) {
  const opts = { root: searchIn, conf: { bus, init, history } }

  // initialize components on load
  component('time', time, opts)
  asyncComponent('masonry', () => import('./transforms/masonry'), opts)
  asyncComponent('date', () => import('./transforms/date'), opts)
  asyncComponent('menu', () => import('./transforms/menu'), opts)
  asyncComponent('dock', () => import('./transforms/dock'), opts)
  asyncComponent('editor', () => import('./transforms/editor'), opts)
  asyncComponent('calendar', () => import('./transforms/calendar'), opts)
  asyncComponent('gallery', () => import('./transforms/gallery'), opts)
  asyncComponent('gallery-editor', () => import('./transforms/gallery-editor'), opts)
  asyncComponent('snake', () => import('./transforms/snake'), opts)
  asyncComponent('openable', () => import('./transforms/openable'), opts)
  asyncComponent('clipboard', () => import('./transforms/clipboard'), opts)
  asyncComponent('carousel', () => import('./transforms/carousel'), opts)
  asyncComponent('conversation', () => import('./transforms/conversation'), opts)
  asyncComponent('keysubmit', () => import('./transforms/keysubmit'), opts)
  asyncComponent('select', () => import('./transforms/select'), opts)
  asyncComponent('publish', () => import('./transforms/publish'), opts)
  asyncComponent('event-time', () => import('./transforms/event-time'), opts)
  asyncComponent('dismissible', () => import('./transforms/dismissible'), opts)
  asyncComponent('autosize', () => import('./transforms/autosize'), opts)
  asyncComponent('cite', () => import('./transforms/cite'), opts)
  asyncComponent('grouplink', () => import('./transforms/grouplink'), opts)
  asyncComponent('image-picker', () => import('./transforms/image-picker'), opts)
  asyncComponent('group-search', () => import('./transforms/group-search'), opts)
  asyncComponent('poll', () => import('./transforms/poll'), opts)
  asyncComponent('poll-editor', () => import('./transforms/poll-editor'), opts)
  asyncComponent('location', () => import('./transforms/location'), opts)
  asyncComponent('poi', () => import('./transforms/poi'), opts)
  asyncComponent('tabs', () => import('./transforms/tabs'), opts)
  asyncComponent('taginput', () => import('./transforms/taginput'), opts)
  asyncComponent('scroll-container', () => import('./transforms/scroll-container'), opts)

  // initialize components not based on component interface
  asyncComponent(
    $$('input:not(.vue-input), select, textarea'),
    () => import('./transforms/input'),
    defaultsDeep({
      conf: { target: el => closest(el, '.form-group') || el },
      name: 'input'
    }, opts)
  )
  asyncComponent(
    $$('blockquote').filter(b => !closest(b, 'blockquote')),
    () => import('./transforms/quote'),
    defaultsDeep({
      name: 'quote'
    }, opts)
  )

  // register popstate handler
  history.mount()
}

init()
