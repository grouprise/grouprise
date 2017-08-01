import { $, replace } from 'luett'
import Drop from 'tether-drop'
import delegate from 'delegate'
import axios from 'axios'
import bel from 'bel'

import { eventedFunction } from '../util/events'
import ImageEditor from '../components/image/editor-image'
import Lightbox from './lightbox'

// create evented functions
const eventedReplace = eventedFunction(replace)

function reload () {
  return axios.get(window.location.href, { responseType: 'document' })
        .then(res => Promise.resolve($('.gallery', res.data)))
}

function createEditor (trigger) {
  const imageEditor = ImageEditor({ tabs: { user: false, content: false } })
  const imageDialog = bel`<div class="editor-dialog">${imageEditor.el}</div>`

  const drop = new Drop({
    target: trigger,
    content: imageDialog,
    position: 'bottom right'
  })

  const listener = delegate(trigger, 'click', function (e) {
    e.preventDefault()
    drop.toggle()
  })

  imageEditor.emitter.on('files:select', () => {
    drop.close()
  })

  return {
    emitter: imageEditor.emitter,
    remove: function () {
      imageEditor.remove()
      listener.destroy()
    }
  }
}

export default (el) => {
  const editorAdd = $("[data-purpose='gallery-add']", el)
  let lightbox = Lightbox(el)

  if (editorAdd) {
    const editor = createEditor(editorAdd)
    editor.emitter.on('files:select', () => {
      reload().then((gallery) => {
        const oldGallery = $('.gallery', el)
        eventedReplace(oldGallery, gallery)
      }).then(() => {
        lightbox.remove()
        lightbox = Lightbox(el)
      })
    })
  }

  return el
}
