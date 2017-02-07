import { gestaltSettings } from '../adapters/api'
import closest from 'closest'
import { remove, addClass } from 'luett'

function on(el, event, callback) {
  el.addEventListener(event, callback, false)
  return {
    destroy() {
      el.removeEventListener(event, callback, false)
    }
  }
}

export default el => {
  const payload = JSON.parse(el.dataset.dismissiblePayload)
  const listener = on(el, 'click', () => {
    const dismissible = closest(el, '.dismissible')
    addClass(dismissible, 'dismissible-pending')
    gestaltSettings.create(payload)
      .then(() => remove(dismissible))
  })

  return {
    remove() {
      listener.destroy()
    }
  }
}
