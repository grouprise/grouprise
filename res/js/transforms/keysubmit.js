import closest from 'closest'
import { keyPressed, on } from 'luett'

const usage = `<span class='pull-right media-instruction'>
    <kbd>Shift</kbd> + <kbd>Enter</kbd> sendet das Formular ab
</span>`

export default el => {
  el.insertAdjacentHTML('afterend', usage)

  const keyDownListener = on(el, 'keydown', keyPressed(13, { shiftKey: true }, event => {
    event.preventDefault()
    closest(el, 'form').dispatchEvent(new window.Event('submit', { bubbles: true, cancelable: true }))
  }))

  return {
    el,
    remove: () => {
      keyDownListener.destroy()
    }
  }
}
