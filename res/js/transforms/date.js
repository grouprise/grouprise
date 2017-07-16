import flatpickr from 'flatpickr'
import locales from 'flatpickr/dist/l10n/de'
import moment from 'moment'
import { includes } from 'lodash'

const { de } = locales

const base = {
  time_24hr: true,
  dateFormat: 'd.m.Y',
  minuteIncrement: 15,
  weekNumbers: true,
  locale: de,
  parseDate: (date) => moment(date, 'DD.MM.YYYY', 'de', true).toDate()
}

export default (el, opts = {}) => {
  const config = Object.assign({}, base, opts, opts.conf)

  if (includes(opts.types, 'datetime')) {
    config.enableTime = true
    config.dateFormat = `${config.dateFormat} H:i:00`
    config.parseDate = (date) => moment(date, 'DD.MM.YYYY HH:mm:ss', 'de', true).toDate()
  }

  const pickr = flatpickr(el, config)
  return {
    pickr,
    remove: () => {
      pickr.destroy()
    }
  }
}
