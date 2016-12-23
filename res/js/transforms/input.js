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

    target.classList.toggle('input-focused', isFocused)
    target.classList.toggle('input-blurred', !isFocused)
  }

  function setType () {
    target.classList.toggle(`input-type-${el.tagName.toLowerCase()}`, true)
  }

  attachAndRun(el, 'input change', setChangedStates)
  attachAndRun(el, 'focus blur', setFocusStates)

  setType()
}
