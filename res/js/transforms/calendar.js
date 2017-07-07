import axios from 'axios'
import { $, getAttr } from 'luett'
import delegate from 'delegate'

const classLoading = 'calendar-loading'

function load (url, selector) {
  return axios.get(url, { responseType: 'document' })
    .then(res => Promise.resolve($(selector, res.data)))
}

function Calendar (el, opts) {
  const calendarId = el.id
  const reinit = opts.conf.init

  function replaceWith (sourceUrl) {
    el.classList.add(classLoading)

    load(sourceUrl, `#${calendarId}`)
      .then(newCalendar => {
        el.innerHTML = newCalendar.innerHTML
        el.classList.remove(classLoading)
        reinit(el)
      })
  }

  const onNavigate = delegate(el, '.calendar-month a', 'click', event => {
    event.preventDefault()
    replaceWith(getAttr(event.delegateTarget, 'href'))
  })

  return {
    remove () {
      onNavigate.destroy()
    }
  }
}

export default (el, opts) => Calendar(el, opts)
