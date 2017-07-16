import axios from 'axios'
import { $, attr, className } from 'luett'
import delegate from 'delegate'

const classLoading = className('calendar-loading')
const href = attr('href')

function load (url, selector) {
  return axios.get(url, { responseType: 'document' })
    .then(res => {
      const el = $(selector, res.data)
      const title = $('title', res.data)
      return Promise.resolve({
        url,
        title: title.innerHTML || '',
        el: el.innerHTML || '',
      })
    })
}

function Calendar (el, opts) {
  const calendarId = el.id
  const calendarEl = () => el.matches('.calendar') ? el : $('.calendar', el)
  const reinit = opts.conf.init

  const history = opts.conf.history.register(`calendar-${calendarId}`, state => {
    replaceWith(state ? state.url : window.location.href, false)
  }, event => event.state === null && window.location.pathname === opts.conf.basepath)

  function replaceWith (sourceUrl, push = true) {
    classLoading.add(calendarEl())

    load(sourceUrl, `#${calendarId}`)
      .then(newCalendar => {
        el.innerHTML = newCalendar.el
        classLoading.remove(calendarEl())
        reinit(el)

        if (push) {
          history.pushState(newCalendar, newCalendar.title, sourceUrl)
        }
      })
  }

  const onNavigate = delegate(el, '.calendar-month a', 'click', event => {
    event.preventDefault()
    replaceWith(href.get(event.delegateTarget))
  })

  return {
    remove () {
      onNavigate.destroy()
      history.destroy()
    }
  }
}

export default (el, opts) => Calendar(el, opts)
