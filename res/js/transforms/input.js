function attachAndRun (target, event, listener) {
  event.split(' ').forEach((event) => event && target.addEventListener(event, listener, false))
  listener.call(target)
}

export default (el, conf = {}) => {
  const target = conf.target || el

  function setChangedStates () {
    const isFilled = el.value.trim() !== ''
    target.classList.toggle('input-filled', isFilled)
    target.classList.toggle('input-empty', !isFilled)
  }

  function setFocusStates () {
    const isFocused = document.activeElement === el

    if (!isFocused && target.classList.contains('input-focused')) {
      target.classList.add('input-had-focus')
    }

    target.classList.toggle('input-focused', isFocused)
    target.classList.toggle('input-blurred', !isFocused)
  }

  function setType () {
    const tagName = el.tagName.toLowerCase()
    const type = el.getAttribute('type')
    target.classList.toggle(`input-type-${tagName !== 'input' ? tagName : type}`, true)
  }

  attachAndRun(el, 'input change', setChangedStates)
  attachAndRun(el, 'focus blur', setFocusStates)

  setType()
}
