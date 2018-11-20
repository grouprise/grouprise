import { $, toggleClass, setAttr, on } from 'luett'
import closest from 'closest'

function addAuthorPinnedListener (el) {
  const authorSelect = $('[data-select-type="author"]', el)
  const pinnedCheck = $('input[name="pinned"]', el)
  const pinnedWrap = closest(pinnedCheck, '.form-group', true)

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
  const form = closest(el, 'form', true)
  const submitButton = $('[data-publish-submit]', el)
  const submitListener = on(form, 'submit', () => {
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
