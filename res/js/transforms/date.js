import Flatpickr from 'flatpickr'
import locales from 'flatpickr/dist/l10n/de'
import moment from 'moment'

const locale = locales.de
locale.firstDayOfWeek = 1
locale.weekAbbreviation = 'KW'

const base = {
  time_24hr: true,
  dateFormat: 'd.m.Y',
  minuteIncrement: 15,
  weekNumbers: true,
  locale: locale,
  parseDate: (date) => moment(date, 'DD.MM.YYYY', 'de', true).toDate()
}

export default (el, opts) => {
  const config = Object.assign({}, base, opts, opts.conf)

  if (opts.isType('datetime')) {
    config.enableTime = true
    config.dateFormat = `${config.dateFormat} H:i:00`
    config.parseDate = (date) => moment(date, 'DD.MM.YYYY HH:mm:ss', 'de', true).toDate()
  }

  return new Flatpickr(el, config)
}
