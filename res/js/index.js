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

function init (searchIn = document) {
    // initialize components on load
  component('date', date, searchIn)
  component('editor', editor, searchIn)
  component('time', time, searchIn)
  component('user-content', userContent, searchIn)
  component('gallery', gallery, searchIn)
  component('snake', snake, searchIn)
  component('openable', openable, searchIn)
  component('clipboard', clipboard, searchIn)
  component('browser-warning', browserWarning, searchIn)
  component('carousel', carousel, searchIn)
  component('tcon', transformIcon, searchIn)

    // initialize components not based on component interface
  mapCall($$('input, textarea'), (el) => input(el, { target: closest(el, '.form-group') }))
}

init()
