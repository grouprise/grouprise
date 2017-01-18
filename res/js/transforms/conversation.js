import delegate from 'delegate'
import { $, getAttr } from 'luett'

function submit (form) {
  return new Promise((resolve, reject) => {
    const url = getAttr(form, 'action', window.location.href)
    const method = getAttr(form, 'method', 'get').toUpperCase()

    const xhr = new window.XMLHttpRequest()
    xhr.onabort = xhr.onerror = reject
    xhr.onreadystatechange = () => {
      if (xhr.readyState === 4) {
        resolve(xhr.responseXML)
      }
    }
    xhr.open(method, url)
    xhr.responseType = 'document'
    xhr.send(new window.FormData(form))
  })
}

function setInactive (form) {
  const btn = $('.btn', form)
  btn.disabled = true
  btn.classList.add('btn-progress')
  $('textarea', form).readOnly = true
}

export default (el, opts) => {
  const reinit = opts.conf.init
  const id = getAttr(el, 'id')

  function replaceContent (content) {
    el.innerHTML = $(`#${id}`, content).innerHTML
  }

  function handleSubmit (event) {
    event.preventDefault()
    setInactive(event.delegateTarget)
    submit(event.delegateTarget)
      .then(replaceContent)
      .then(() => reinit(el))
      .then(() => $('form textarea', el).focus())
  }

  const destroySubmitListener = delegate(el, 'form', 'submit', handleSubmit)

  return {
    el,
    remove: () => {
      destroySubmitListener()
    }
  }
}
