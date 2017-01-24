import { $, getAttr, remove } from 'luett'
import bel from 'bel'
import EventEmitter from 'eventemitter3'

import { get as getImages, create as createImage } from '../adapters/image'
import pickii from './pickii'
import filePicker from './file-picker'
import tabbed from './tabbed'

const contentId = getAttr($("[name='content_id']"), 'value', false)

function upload (files) {
  const uploader = createImage({ contentId })
  const uploads = files.map((file) => {
    return uploader({
      content: file
    })
  })

  return Promise.all(uploads)
}

function dummyAdapter () {
  return Promise.resolve([])
}

function createFilePicker (emitter) {
  return filePicker({
    accept: ['image/png', 'image/gif', 'image/jpeg', 'capture=camera'],
    multiple: true,
    callback: (files) => {
      upload(files)
        .then((files) => {
          emitter.emit('files:select', files)
          emitter.emit('files:add', files)
        })
    },
    trigger: bel`<button type="button" class="btn btn-link btn-sm">
    <i class="sg sg-add"></i> Hinzufügen
</button>`
  })
}

function createContentImageView (emitter) {
  return pickii({
    emit: emitter.emit.bind(emitter),
    adapter: contentId ? getImages({
      filters: { content: contentId }
    }) : dummyAdapter
  })
}

function createUserImageView (emitter) {
  return pickii({
    emit: emitter.emit.bind(emitter),
    adapter: window.app.conf.gestalt.id ? getImages({
      filters: { creator: window.app.conf.gestalt.id }
    }) : dummyAdapter
  })
}

function createTabbed (emitter, tabConfig = {}) {
  const opts = Object.assign({}, {user: true, content: true}, tabConfig)
  const tabs = []

  if (opts.content) {
    const contentImageView = createContentImageView(emitter)
    emitter.on('files:add', contentImageView.refresh)
    tabs.push({
      content: contentImageView.el,
      label: bel`<span>Beitragsbilder</span>`
    })
  }

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

  const imageEditor = bel`<div class="editor-images">
    <div class="btn-toolbar btn-toolbar-spread">
        <h3>Bilder</h3>
        ${createFilePicker(emitter).el}
    </div>
    ${createTabbed(emitter, opts.tabs).el}
</div>`

  iface.remove = function () {
    remove(imageEditor)
  }

  iface.emitter = emitter
  iface.el = imageEditor

  return iface
}
