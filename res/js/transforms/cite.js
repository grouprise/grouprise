import { includes } from 'lodash'
import { on, $, getAttr } from 'luett'
import stroll from 'stroll.js'
import getInputSelection from 'get-input-selection'

const DOMParser = window.DOMParser
export const EVENT_CITE = 'component:cite:cite'

function decode (input) {
  const doc = new DOMParser().parseFromString(input, 'text/html')
  return doc.documentElement.textContent
}

function citeSource (el, opts) {
  const { bus } = opts.conf

  const clickListener = on(el, 'click', event => {
    event.preventDefault()

    const target = $(`${event.target.getAttribute('href')} .media-body`)
    const id = getAttr(target, 'data-id')
    const author = getAttr(target, 'data-author')
    const permalink = getAttr(target, 'data-permalink')
    const text = decode(JSON.parse($('[data-original-content]', target).textContent))
    const formattedText = (text + (author ? `\n — [${author}](${permalink})` : '')).replace(/^/gm, '> ')
    const data = { id, author, permalink, text, formattedText }

    bus.emit(EVENT_CITE, data)
  })

  return {
    remove () {
      clickListener.destroy()
    }
  }
}

function citeSink (el, opts) {
  const { bus } = opts.conf

  const citeListener = bus.on(EVENT_CITE, data => {
    stroll(el, { allowInvalidPositions: true })
    const { end: position } = getInputSelection(el)
    const pre = el.value.substr(0, position)
    const post = el.value.substr(position)
    el.value = [pre, data.formattedText, post].join('\n')
    el.dispatchEvent(new window.Event('input'))
  })

  return {
    remove () {
      citeListener.destroy()
    }
  }
}

function citeInReplyTo (el, opts) {
  const { bus } = opts.conf

  const citeListener = bus.on(EVENT_CITE, data => {
    el.value = data.id
  })

  return {
    remove () {
      citeListener.destroy()
    }
  }
}

export default (el, opts) => {
  return includes(opts.types, 'sink')
    ? citeSink(el, opts)
    : includes(opts.types, 'in-reply-to')
    ? citeInReplyTo(el, opts)
    : citeSource(el, opts)
}
