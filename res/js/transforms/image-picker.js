import Vue from 'vue'
import { $, remove, insertElement } from 'luett'
import { image as imageAdapter } from '../adapters/api'
import DomAdapter from '../adapters/dom'
import UploaderFactory from '../util/uploader'

const uploader = UploaderFactory(imageAdapter)

export default el => {
  const store = DomAdapter(el)
  const ImagePicker = Vue.component('sg-image-picker')
  const help = $('.help-block', el.parentNode)

  // create container
  const container = document.createElement('div')
  container.id = `${el.id}-container`
  insertElement.after(el, container)
  el.style.display = 'none'
  if (help) help.style.display = 'none'

  // create component state
  const state = {
    image: null,
    help: help ? help.textContent.trim() : null,
    uploader
  }

  function updateState (id) {
    if (!id) return

    imageAdapter.get({ id })
      .then(images => {
        state.image = images[0]
      })
      .catch(() => { state.image = null })
  }

  const vue = new Vue({
    el: `#${container.id}`,
    data: state,
    render (h) {
      return h(ImagePicker, {
        props: {
          help: this.help,
          image: this.image,
          uploader: this.uploader
        },
        on: {
          input (images) {
            const image = images[0]
            const valueObj = { value: image.id, name: image.title }
            store.set(valueObj, true)
            updateState(valueObj.value)
          }
        }
      })
    }
  })

  updateState(store.get().value)

  return {
    remove () {
      vue.$destroy()
      remove(container)
      if (help) help.style.removeProperty('display')
    }
  }
}
