import moment from 'moment'

// load locale files
import 'moment/locale/de'

// initialize locale
moment.locale('de')

const timeInstances = []

const transforms = {
  'from': {
    apply(el, opts) {
      el.innerHTML = moment(el.getAttribute('datetime')).from(opts.conf.ref || new Date())
    }
  },
  'to': {
    apply(el, opts) {
      el.innerHTML = moment(opts.conf.ref || new Date()).to(el.getAttribute('datetime'))
    }
  },
  'days-until': {
    apply(el, opts) {
      const days = moment(el.getAttribute('datetime')).diff(opts.conf.ref || new Date(), 'days')
      el.setAttribute('data-days', days)
      el.innerHTML = moment(el.getAttribute('datetime')).diff(opts.conf.ref || new Date(), 'days')
    },
    destroy(el) {
      el.removeAttribute('data-days')
    }
  }
}

function transformAll () {
  timeInstances.forEach(time => time.transform())
}

function Time (el, opts) {
  const origContent = el.innerHTML
  const transform = transforms[opts.conf.transform]
  const self = {
    remove() {
      if (transform.destroy) {
        transform.destroy(el, opts)
      }
      el.innerHTML = origContent
      const index = timeInstances.indexOf(self);
      timeInstances.splice(index, 1);
    },
    transform() {
      transform.apply(el, opts)
    }
  }
  timeInstances.push(self)
  self.transform()
  return self
}

Time.DEFAULTS = {
  'transform': 'from'
}

setInterval(transformAll, 60 * 1000)

export default Time
