import { gestaltSettings } from '../adapters/api'
import closest from 'closest'
import { remove, addClass, setAttr, on } from 'luett'

export default el => {
  const payload = JSON.parse(el.dataset.dismissiblePayload)
  const listener = on(el, 'click', () => {
    const dismissible = closest(el, '.dismissible')
    addClass(dismissible, 'dismissible-pending')
    setAttr(el, 'disabled', 'disabled')
    gestaltSettings.create(payload)
      .then(() => remove(dismissible))
  })

  return {
    remove () {
      listener.destroy()
    }
  }
}
