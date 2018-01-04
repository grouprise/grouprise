import { setAttr, hasAttr, on } from 'luett'
import Drop from 'tether-drop'
import bel from 'bel'
import closest from 'closest'
import { throttle } from 'lodash'

import { EVENT_CITE } from './cite'
import ImageEditor from '../components/image/editor-image'
import createOptions from './editor.options'

const HEADER_OFFSET = 60
const imageEditor = ImageEditor()
const imageDialog = bel`<div class="editor-dialog">${imageEditor.el}</div>`

function createStandardEventEmitter (obj) {
  return {
    addEventListener: obj.on.bind(obj),
    removeEventListener: obj.off.bind(obj)
  }
}

function quote (text) {
  return text.split('\n')
        .map(line => `> ${line}`)
        .join('\n')
}

function editor (CodeMirror, SimpleMDE, el, opts) {
  // force the codemirrors inputStyle to textarea, to workaround
  // contentEditable bugs on mobile devices
  CodeMirror.defaults.inputStyle = 'textarea'

  // find editor container. we rely on existing markup here. maybe it’s a
  // good idea to create this one here
  const containerEl = closest(el, '.editor-container')
  containerEl.classList.add('editor-container-ready')

  const { bus } = opts.conf
  const isRequired = hasAttr(el, 'required')
  const form = closest(el, 'form')
  const editor = new SimpleMDE(createOptions(el, SimpleMDE))

  // create our drop container for images
  // TODO this should be replaced with popper.js
  const drop = new Drop({
    target: editor.toolbarElements['image'],
    content: imageDialog,
    openOn: 'click',
    position: 'bottom right',
    tetherOptions: {
      constraints: [{
        to: 'window',
        pin: true
      }]
    }

  })

  const wrapper = editor.codemirror.display.wrapper
  const toolbar = editor.gui.toolbar
  const toolbarRect = toolbar.getBoundingClientRect()
  const toolbarTop = document.documentElement.scrollTop + toolbarRect.y
  const codemirrorEvents = createStandardEventEmitter(editor.codemirror)

  // add scroll-listener for positioning the
  // editor-toolbar while scrolling
  const scrollListener = on(window, 'scroll', throttle(() => {
    const wrapperRect = wrapper.getBoundingClientRect()
    const scrollTop = document.documentElement.scrollTop
    const headerTop = scrollTop + HEADER_OFFSET
    const wrapperTop = scrollTop + wrapperRect.y + wrapperRect.height - toolbarRect.height
    const offset = headerTop > toolbarTop
      ? Math.min(wrapperTop - toolbarTop, Math.abs(toolbarTop - headerTop + 2)) : 0
    toolbar.style.transform = offset > 0 ? `translateY(${offset}px)` : ''
  }, 250), { passive: true })

  // create focusListener to move the toolbar into the current scrollPosition
  // whenever the editor is focused
  const focusListener = on(codemirrorEvents, ['focus', 'blur'], () => {
    containerEl.classList.toggle('editor-container-active', editor.codemirror.hasFocus())
  })

  // prevent users from accidentally leaving the page when
  // they’ve changed the content of the editor
  let editorHasChanged = false
  const changeListener = on(codemirrorEvents, 'change', () => {
    editorHasChanged = true
  })
  const beforeUnloadListener = on(window, 'beforeunload', event => {
    const message = 'Du hast Änderungen am Inhalt vorgenommen. Bist du sicher, dass du die ' +
      'Seite verlassen willst?'
    if (editorHasChanged) {
      event.returnValue = message
      return message
    }
  })

  // whenever images have been selected and uploaded insert image
  // markdown image references into the editor
  imageEditor.emitter.on('files:select', files => {
    const text = editor.codemirror.getSelection()
    const code = files.map((file) => {
      return `![${(text.length > 0) ? text : file.label}](${file.content})`
    }).join('\n')

    editor.codemirror.doc.replaceSelection(code)
    drop.close()
  })

  // whenever images have been added, append hidden `images` fields for
  // to the form. this way we associate content with images
  // TODO are we still assigning images to content in any way?
  imageEditor.emitter.on('files:add', files => {
    files.forEach((file) => {
      form.appendChild(bel`<input type="hidden" name="images" value="${file.id}">`)
    })
  })

  // when someone clicks on a cite link an event is send through our
  // application bus. we use this event to place the cited content
  // into our editor with markdown quotes
  const citeListener = bus.on(EVENT_CITE, data => {
    editor.codemirror.doc.replaceSelection(quote(data.formattedText))
  })

  // we remove the required attribute from the original textarea
  // because otherwise the browser’s html5 validation might might chip in
  // when the form is submitted and would prevent the form from being sent
  if (isRequired) {
    el.removeAttribute('required')
  }

  return {
    editor,
    remove: () => {
      if (isRequired) setAttr(el, 'required', 'required')
      editor.toTextArea()
      citeListener.destroy()
      scrollListener.destroy()
      focusListener.destroy()
      changeListener.destroy()
      beforeUnloadListener.destroy()
    }
  }
}

export default (el, opts) => {
  return Promise.all([
    System.import('codemirror'),
    System.import('simplemde')
  ]).then(deps => {
    const [CodeMirror, SimpleMDE] = deps
    return Promise.resolve(editor(CodeMirror, SimpleMDE, el, opts))
  })
}
