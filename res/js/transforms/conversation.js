import delegate from 'delegate'
import { $, getAttr } from 'luett'
import { danger } from '../util/notify'

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

function setActive (form) {
  const btn = $('.btn', form)
  btn.disabled = false
  btn.classList.remove('btn-progress')
  $('textarea', form).readOnly = false
}

export default (el, opts) => {
  const reinit = opts.conf.init
  const id = getAttr(el, 'id')

  function replaceContent (content) {
    el.innerHTML = $(`#${id}`, content).innerHTML
  }

  function onFailure() {
    danger('Bei der Verarbeitung deines Beitrags ist ein Fehler aufgetreten! Sorry 😔')
    setActive($('form', el))
  }

  function handleSubmit (event) {
    event.preventDefault()
    setInactive(event.delegateTarget)
    submit(event.delegateTarget)
      .then(replaceContent)
      .then(() => reinit(el))
      .then(() => $('form textarea', el).focus())
      .catch(onFailure)
  }

  const submitListener = delegate(el, 'form', 'submit', handleSubmit)

  return {
    el,
    remove: () => {
      submitListener.destroy()
    }
  }
}
