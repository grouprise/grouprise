import flatpickr from 'flatpickr/src/flatpickr'
import moment from 'moment'

flatpickr.init.prototype.l10n.months.longhand = [
  'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli',
  'August', 'September', 'Oktober', 'November', 'Dezember'
]

flatpickr.init.prototype.l10n.months.shorthand = [
  'Jan', 'Feb', 'März', 'Apr', 'Mai', 'Juni',
  'Juli', 'Aug', 'Sept', 'Okt', 'Nov', 'Dez'
]

flatpickr.init.prototype.l10n.weekdays.longhand = [
  'Sonntag', 'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag'
]

flatpickr.init.prototype.l10n.weekdays.shorthand = [
  'So', 'Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa'
]

flatpickr.init.prototype.l10n.firstDayOfWeek = 1

const base = {
  time_24hr: true,
  dateFormat: 'd.m.Y',
  minuteIncrement: 15,
  parseDate: (date) => moment(date, 'DD.MM.YYYY', 'de', true).toDate()
}

export default (el, opts) => {
  const config = Object.assign({}, base, opts, opts.conf)

  if (opts.isType('datetime')) {
    config.enableTime = true
    config.dateFormat = `${config.dateFormat} H:i:00`
    config.parseDate = (date) => moment(date, 'DD.MM.YYYY HH:mm:ss', 'de', true).toDate()
  }

  return flatpickr(el, config)
}
