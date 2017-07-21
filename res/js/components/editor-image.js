import { remove, toggleClass } from 'luett'
import bel from 'bel'
import EventEmitter from 'eventemitter3'

import UploaderFactory from '../util/uploader'
import { image as adapter } from '../adapters/api'
import pickii from './pickii'
import filePicker from './file-picker'
import tabbed from './tabbed'
import progress from './progress'

const uploader = UploaderFactory(adapter)
let processIds = 0

function dummyAdapter () {
  return Promise.resolve([])
}

function createFilePicker (emitter) {
  return filePicker({
    accept: ['image/png', 'image/gif', 'image/jpeg', 'capture=camera'],
    multiple: true,
    callback: (files) => {
      const processId = processIds++
      emitter.emit('files:upload', { files, processId })
      uploader.upload(files, progress => emitter.emit('files:progress', { progress, processId }))
        .then((files) => {
          emitter.emit('files:select', files)
          emitter.emit('files:add', files)
          emitter.emit('files:done', { files, processId })
        })
    },
    trigger: bel`<button type="button" class="btn btn-link btn-sm">
    <i class="sg sg-add"></i> Hinzufügen
</button>`
  })
}

function createUserImageView (emitter) {
  const creator = window.app.conf.gestalt.id
  return pickii({
    emit: emitter.emit.bind(emitter),
    adapter: creator ? () => adapter.get({creator}) : dummyAdapter
  })
}

function createTabbed (emitter, tabConfig = {}) {
  const opts = Object.assign({}, {user: true}, tabConfig)
  const tabs = []

  if (opts.user) {
    const userImageView = createUserImageView(emitter)
    emitter.on('files:add', userImageView.refresh)
    tabs.push({
      content: userImageView.el,
      label: bel`<span>Deine Bilder</span>`
    })
  }

  return tabbed({tabs})
}

export default (opts = {}) => {
  const iface = {}
  const emitter = new EventEmitter()
  let progressBar

  const imageEditor = bel`<div class="editor-images">
    <div class="btn-toolbar btn-toolbar-spread">
        <h3>Bilder</h3>
        ${createFilePicker(emitter).el}
    </div>
    ${createTabbed(emitter, opts.tabs).el}
</div>`

  iface.remove = function () {
    remove(imageEditor)
    if (progressBar) {
      progressBar.destroy()
    }
  }

  iface.emitter = emitter
  iface.el = imageEditor

  emitter.on('files:upload', event => {
    toggleClass(imageEditor, 'editor-images-upload', true)
    progressBar = progress({
      description: `${event.files.length} ${event.files.length === 1 ? 'Bild wird' : 'Bilder werden'} hochgeladen`
    })
    imageEditor.appendChild(progressBar.el)
  })

  emitter.on('files:progress', event => {
    progressBar.setProgress(event.progress.complete)
  })

  emitter.on('files:done', () => {
    progressBar.remove()
    remove(progressBar.el)
    toggleClass(imageEditor, 'editor-images-upload', false)
  })

  return iface
}
