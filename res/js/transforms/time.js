import moment from 'moment'

// load locale files
import 'moment/locale/de'

// initialize locale
moment.locale('de')

const transforms = []

function transformNow (index = null) {
  if (index) {
    transforms[index]()
  } else {
    transforms.forEach((transform) => transform())
  }
}

function addTransform (transform) {
  const index = transforms.push(transform) - 1
  transformNow(index)
  return transform
}

function transformFrom (el, opts) {
  return () => {
    el.innerHTML = moment(el.getAttribute('datetime')).from(opts.conf.ref || new Date())
  }
}

function transformTo (el, opts) {
  return () => {
    el.innerHTML = moment(opts.conf.ref || new Date()).to(el.getAttribute('datetime'))
  }
}

function transformDaysUntil (el, opts) {
  return () => {
    const days = moment(el.getAttribute('datetime')).diff(opts.conf.ref || new Date(), 'days')
    el.setAttribute('data-days', days)
    el.innerHTML = moment(el.getAttribute('datetime')).diff(opts.conf.ref || new Date(), 'days')
  }
}

function createTransform (el, opts) {
  if (opts.isType('from')) {
    return addTransform(transformFrom(el, opts))
  }

  if (opts.isType('to')) {
    return addTransform(transformTo(el, opts))
  }

  if (opts.isType('days-until')) {
    return addTransform((transformDaysUntil(el, opts)))
  }
}

setInterval(transformNow, 60 * 1000)

export default createTransform
