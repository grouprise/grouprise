import { includes } from 'lodash'
import { on, $, getAttr } from 'luett'
import getInputSelection from 'get-input-selection'

export const EVENT_CITE = 'component:cite:cite'

function citeSource(el, opts) {
  const { bus } = opts.conf

  const clickListener = on(el, 'click', event => {
    event.preventDefault()

    const target = $(`${event.target.getAttribute('href')} .media-body`)
    const author = getAttr(target, 'data-author')
    const permalink = getAttr(target, 'data-permalink')
    const text = target.innerText
    const formattedText = text + (author ? `\n — [${author}](${permalink})` : '')
    const data = { author, permalink, text, formattedText }

    bus.emit(EVENT_CITE, data)
  })

  return {
    remove() {
      clickListener.destroy()
    }
  }
}

function citeSink(el, opts) {
  const { bus } = opts.conf

  const citeListener = bus.on(EVENT_CITE, data => {
    const { end: position } = getInputSelection(el)
    const pre = el.value.substr(0, position)
    const post = el.value.substr(position)
    el.value = [pre, data.formattedText, post].join('\n')
    el.dispatchEvent(new window.Event('input'))
  })

  return {
    remove() {
      citeListener.destroy()
    }
  }
}

export default (el, opts) => {
  return includes(opts.types, 'sink')
    ? citeSink(el, opts)
    : citeSource(el, opts)
}
