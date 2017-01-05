import { replace, remove, getAttr } from 'luett'
import delegate from 'delegate'
import bel from 'bel'

function dummy () {
  return bel`<div class="pickii-dummy">Keine Bilder verfügbar</div>`
}

function picker () {
  return bel`<div class="pickii">${dummy()}</div>`
}

function pickerImages (images) {
  if (images.length) {
    return bel`<ol class="pickii-images">${images.map(pickerImage)}</ol>`
  } else {
    return dummy()
  }
}

function pickerImage (image) {
  return bel`<li>
    <button class="pickii-image"
    data-image="${JSON.stringify(image)}"
    type="button"
    style="background-image: url(${image.content})"
    title="${image.label}"></button>
</li>`
}

export default (opts) => {
  const iface = {}
  const el = picker()

  const listener = delegate(el, '.pickii-image', 'click', (e) => {
    opts.emit('files:select', [JSON.parse(getAttr(e.delegateTarget, 'data-image'))])
  })

  iface.refresh = function () {
    opts.adapter()
            .then((images) => {
              replace(el.children[0], pickerImages(images, opts.emit))
            })
  }

  iface.remove = function () {
    listener.destroy()
    remove(el)
  }

  iface.el = el

  iface.refresh()

  return iface
}
