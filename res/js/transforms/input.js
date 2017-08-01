function attachAndRun (target, event, listener, capture = false) {
  const events = event.split(' ')
  events.forEach((event) => event && target.addEventListener(event, listener, capture))
  listener.call(target)
  return {
    destroy () {
      events.forEach((event) => event && target.removeEventListener(event, listener, capture))
    }
  }
}

function getType (el) {
  const tagName = el.tagName.toLowerCase()
  const type = el.getAttribute('type')
  return `input-type-${tagName !== 'input' ? tagName : type}`
}

function input (el, opts = {}) {
  const target = opts.conf.target ? opts.conf.target(el) : el

  function setChangedStates (event) {
    const isFilled = el.value.trim() !== ''
    target.classList.toggle('input-filled', isFilled)
    target.classList.toggle('input-empty', !isFilled)

    if (event) {
      target.classList.toggle('input-changed', true)
    }
  }

  function setFocusStates () {
    const isFocused = document.activeElement === el

    if (!isFocused && target.classList.contains('input-focused')) {
      target.classList.add('input-had-focus')
    }

    target.classList.toggle('input-focused', isFocused)
    target.classList.toggle('input-blurred', !isFocused)
  }

  const inputListeners = attachAndRun(el, 'input change', setChangedStates)
  const focusListeners = attachAndRun(el, 'focus blur', setFocusStates)

  const typeClass = getType(el)
  target.classList.toggle(typeClass, true)

  return {
    remove () {
      inputListeners.destroy()
      focusListeners.destroy()
      target.classList.remove(
        'input-filled',
        'input-empty',
        'input-changed',
        'input-focused',
        'input-had-focus',
        'input-blurred',
        typeClass
      )
    }
  }
}

input.NAME = 'input'

export default input
