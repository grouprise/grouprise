import { $, toggleClass, setAttr } from 'luett'
import closest from 'closest'

function on (el, event, callback, useCapture = false) {
  el.addEventListener(event, callback, useCapture)
  return {
    destroy: () => el.removeEventListener(event, callback, useCapture)
  }
}

function addAuthorPinnedListener (el) {
  const authorSelect = $('[data-select-type="author"]', el)
  const pinnedCheck = $('input[name="pinned"]', el)
  const pinnedWrap = closest(pinnedCheck, '.form-group')

  if (!authorSelect || !pinnedWrap) return

  function setState () {
    toggleClass(pinnedWrap, 'form-group-unused', !authorSelect.value)
  }

  const authorSelectListener = on(authorSelect, 'change', setState)
  setState()

  return {
    remove: () => {
      authorSelectListener.destroy()
    }
  }
}

function addPublishListener (el) {
  const form = closest(el, 'form')
  const submitButton = $('[type="submit"]', el)
  const submitListener = on(form, 'submit', event => {
    event.preventDefault()
    toggleClass(submitButton, 'btn-progress', true)
    setAttr(submitButton, 'disabled', 'disabled')
  })

  return {
    remove: () => {
      submitListener.destroy()
    }
  }
}

export default el => {
  const components = [
    addAuthorPinnedListener(el),
    addPublishListener(el)
  ]

  return {
    remove: () => {
      components.forEach(cmp => cmp.remove())
    }
  }
}
