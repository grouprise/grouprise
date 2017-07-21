import closest from 'closest'
import { $, $$, remove, insertElement } from 'luett'
import bel from 'bel'
import Vue from 'vue'
import { image } from '../adapters/api'
import GalleryCreator from '../content/components/gallery-editor.vue'

export default el => {
  const images = []
  const container = document.createElement('div')
  const label = $('label', closest(el, '.form-group'))
  container.id = `${el.id}-container`
  insertElement.after(el, container)
  el.style.display = 'none'
  label.style.display = 'none'

  const emitChange = () => el.dispatchEvent(new window.Event('change'))

  const editor = new Vue({
    el: `#${container.id}`,
    render (h) {
      return h(GalleryCreator, {
        props: {
          images: this.images,
          imagesReady: this.imagesReady
        },
        on: {
          add: this.addImages,
          remove: this.removeImage
        }
      })
    },
    data: {
      images,
      imagesReady: true
    },
    methods: {
      addImages (newImages) {
        newImages.forEach(image => {
          el.appendChild(bel`<option value='${image.id}' selected>${image.label}</option>`)
          images.push(image)
        })
        emitChange()
      },
      removeImage (image) {
        const option = $(`option[value='${image.id}'][selected]`, el)
        const index = images.indexOf(image)
        if (index > -1) images.splice(index, 1)
        if (option) option.selected = false
        emitChange()
      }
    }
  })

  const selectedImages = $$('option', el)
    .filter(opt => opt.selected)
    .map(opt => opt.value)

  if (selectedImages.length > 0) {
    editor.imagesReady = false
    image.get({ id: selectedImages.join(',') })
      .then(files => {
        editor.imagesReady = true
        files.forEach(file => images.push(file))
      })
      .catch(e => {
        console.error(e)
      })
  }

  return {
    remove () {
      if (editor) editor.$destroy()
      if (container) {
        remove(container)
        el.style.display = null
        label.style.display = null
      }
    }
  }
}
