import axios from 'axios'
import { $, attr, className } from 'luett'
import delegate from 'delegate'

const classLoading = className('calendar-loading')
const href = attr('href')

function load (url, selector) {
  return axios.get(url, { responseType: 'document' })
    .then(res => Promise.resolve($(selector, res.data)))
}

function Calendar (el, opts) {
  const calendarId = el.id
  const reinit = opts.conf.init

  function replaceWith (sourceUrl) {
    classLoading.add(el)

    load(sourceUrl, `#${calendarId}`)
      .then(newCalendar => {
        el.innerHTML = newCalendar.innerHTML
        classLoading.remove(el)
        reinit(el)
      })
  }

  const onNavigate = delegate(el, '.calendar-month a', 'click', event => {
    event.preventDefault()
    replaceWith(href.get(event.delegateTarget))
  })

  return {
    remove () {
      onNavigate.destroy()
    }
  }
}

export default (el, opts) => Calendar(el, opts)
