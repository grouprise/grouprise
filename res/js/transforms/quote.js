import { insertElement, on, remove } from 'luett'

function createTestNode () {
  const el = document.createElement('blockquote')
  el.textContent = 'test'
  el.style.padding = '0 !important'
  el.style.border = 'none !important'
  return el
}

function createExtendButton () {
  const btn = document.createElement('button')
  btn.classList.add('btn', 'btn-text', 'btn-sm', 'quote-extend')
  btn.textContent = 'Vollständiges Zitat anzeigen…'
  return btn
}

function quote (el) {
  const testNode = insertElement.before(el, createTestNode())
  const lineHeight = testNode.getBoundingClientRect().height
  const elHeight = el.getBoundingClientRect().height
  const maxHeight = lineHeight * 3 + 40
  let listener
  let btn

  remove(testNode)

  function shorten () {
    el.style.maxHeight = `${maxHeight}px`
    el.classList.add('quote-shortened')
    btn = createExtendButton()
    listener = on(btn, 'click', unshorten)
    el.appendChild(btn)
  }

  function unshorten () {
    el.style.maxHeight = null
    el.classList.remove('quote-shortened')
    listener.destroy()
    remove(btn)
  }

  if (elHeight > maxHeight) {
    shorten()
  }

  return { remove: unshorten }
}

quote.NAME = 'quote'

export default quote
