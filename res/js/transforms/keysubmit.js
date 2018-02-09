import bel from 'bel'
import closest from 'closest'
import { insertElement, remove, keyPressed, on } from 'luett'

function usage () {
  return (
    bel`<span class='pull-right media-instruction'>
        <kbd><kbd>Strg</kbd> + <kbd>Enter</kbd></kbd> schickt Deine Nachricht ab
    </span>`
  )
}

export default el => {
  const instructions = insertElement.after(el, usage())

  const keyDownListener = on(el, 'keydown', keyPressed(13, { ctrlKey: true }, event => {
    event.preventDefault()
    const submitEvent = new window.Event('submit', { bubbles: true, cancelable: true })
    const form = closest(el, 'form')
    const submitter = form.querySelector('button[type="submit"], input[type="submit"]')

    if (submitter) {
      submitter.click()
    } else {
      form.dispatchEvent(submitEvent)
    }
  }))

  return {
    el,
    remove: () => {
      keyDownListener.destroy()
      remove(instructions)
    }
  }
}
