import bel from 'bel'
import closest from 'closest'
import { insertElement, remove, keyPressed, on } from 'luett'

function usage () {
  return (
    bel`<span class='pull-right media-instruction'>
        <kbd>Shift</kbd> + <kbd>Enter</kbd> sendet das Formular ab
    </span>`
  )
}

export default el => {
  const instructions = insertElement.after(el, usage())

  const keyDownListener = on(el, 'keydown', keyPressed(13, { shiftKey: true }, event => {
    event.preventDefault()
    closest(el, 'form').dispatchEvent(new window.Event('submit', { bubbles: true, cancelable: true }))
  }))

  return {
    el,
    remove: () => {
      keyDownListener.destroy()
      remove(instructions)
    }
  }
}
