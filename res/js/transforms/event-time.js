import { $, hasAttr, remove, insertElement } from 'luett'
import Vue from 'vue'
import moment from 'moment'

import EventTime from '../content/components/event-time.vue'

const timeFormat = 'DD.MM.YYYY HH:mm:ss'

const convertDate = (value, format = timeFormat) => {
  return !value || !moment(value, format, true).isValid()
    ? null : moment(value, format).toDate()
}

export default el => {
  const container = document.createElement('div')
  container.id = `${el.id}-container`
  insertElement.after(el, container)
  el.style.display = 'none'

  const elStart = $('#id_time', el)
  const elEnd = $('#id_until_time', el)
  const elAllDay = $('#id_all_day', el)

  const vue = new Vue({
    el: `#${container.id}`,
    render (h) {
      return h(EventTime, {
        props: {
          start: this.start,
          end: this.end,
          allDay: this.allDay
        },
        on: {
          change: this.set
        }
      })
    },
    data: {
      start: convertDate(elStart.value),
      end: convertDate(elEnd.value),
      allDay: hasAttr(elAllDay, 'checked')
    },
    methods: {
      set (data) {
        elStart.value = data.start ? moment(data.start).format(timeFormat) : ''
        elEnd.value = data.end ? moment(data.end).format(timeFormat) : ''
        elAllDay.checked = !!data.allDay
        Object.assign(this, data)
      }
    }
  })

  return {
    vue,
    remove () {
      vue.$destroy()
      remove(container)
    }
  }
}
