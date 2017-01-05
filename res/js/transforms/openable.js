import { $ } from 'luett'

function on (el, event, listener, capture = false) {
  el.addEventListener(event, listener, capture)
  return () => el.removeListener(event, listener, capture)
}

function createListener (el, state) {
  const set = (value) => function () { state.isCurrent = value }

  const setActive = on(el, 'mouseenter', set(true))
  const setInactive = on(el, 'mouseleave', set(false))

  return () => {
    setActive()
    setInactive()
  }
}

export default (el, opts) => {
  const target = $(opts.conf.target)
  const state = { isCurrent: false, isActive: !!opts.conf.isActive }

  const sourceListener = createListener(el, state)
  const targetListener = createListener(target, state)
  const triggerListener = on(el, 'click', () => { state.isActive = !state.isActive })
  const documentListener = on(document.documentElement, 'click', () => {
    if (!state.isCurrent && state.isActive) {
      el.click()
    }
  })

  return {
    remove: () => {
      sourceListener()
      targetListener()
      triggerListener()
      documentListener()
    }
  }
}
