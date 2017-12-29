import { $, setAttr, hasAttr, on } from 'luett'
import Drop from 'tether-drop'
import bel from 'bel'
import closest from 'closest'
import { throttle } from 'lodash'

import { markdown } from '../adapters/api'
import { EVENT_CITE } from './cite'
import ImageEditor from '../components/image/editor-image'

const HEADER_OFFSET = 60
const imageEditor = ImageEditor()
const imageDialog = bel`<div class="editor-dialog">${imageEditor.el}</div>`

function quote (text) {
  return text.split('\n')
        .map(line => `> ${line}`)
        .join('\n')
}

function createStandardEventEmitter (obj) {
  return {
    addEventListener: obj.on.bind(obj),
    removeEventListener: obj.off.bind(obj)
  }
}

function editor (CodeMirror, SimpleMDE, el, opts) {
  CodeMirror.defaults.inputStyle = 'textarea'

  const containerEl = closest(el, '.editor-container')
  containerEl.classList.add('editor-container-ready')

  const { bus } = opts.conf
  const isRequired = hasAttr(el, 'required')
  const form = closest(el, 'form')
  const editor = new SimpleMDE({
    autoDownloadFontAwesome: false,
    element: el,
    forceSync: true,
    parsingConfig: {
      allowAtxHeaderWithoutSpace: true,
      strikethrough: false
    },
    promptTexts: {
      link: 'Adresse des Linkziels (URL):',
      image: 'Adresse des Bildes (URL):'
    },
    promptURLs: true,
    shortcuts: {
      'toggleBold': 'Ctrl-B',
      'toggleItalic': 'Ctrl-I',
      'undo': 'Ctrl-Z',
      'redo': 'Ctrl-Y',
      'toggleUnorderedList': 'Shift-F12',
      'toggleOrderedList': 'F12',
      'toggleHeading2': 'Ctrl-2',
      'toggleHeading3': 'Ctrl-3'
    },
    spellChecker: false,
    status: false,
    tabSize: 4,
    previewRender: function (plainText, preview) {
      markdown.parse(plainText)
        .then(
          content => { preview.innerHTML = `<div class="content-body">${content}</div>` },
          () => { preview.innerHTML = `<p class="disclaimer">Fehler beim Laden der Vorschau</p>` }
        )

      return 'Lade Vorschau...'
    },
    toolbar: [
      {
        name: 'undo',
        action: SimpleMDE.undo,
        className: 'fa fa-undo no-disable',
        title: 'Rückgängig'
      },
      {
        name: 'redo',
        action: SimpleMDE.redo,
        className: 'fa fa-repeat no-disable',
        title: 'Wiederholen'
      },
      '|',
      {
        name: 'italic',
        action: SimpleMDE.toggleItalic,
        className: 'fa fa-italic',
        title: 'Kursiv'
      },
      {
        name: 'bold',
        action: SimpleMDE.toggleBold,
        className: 'fa fa-bold',
        title: 'Fett'
      },
      '|',
      {
        name: 'blockquote',
        action: SimpleMDE.toggleBlockquote,
        className: 'fa fa-quote-left',
        title: 'Zitat'

      },
      {
        name: 'unordered-list',
        action: SimpleMDE.toggleUnorderedList,
        className: 'fa fa-list-ul',
        title: 'Einfache Liste'
      },
      {
        name: 'ordered-list',
        action: SimpleMDE.toggleOrderedList,
        className: 'fa fa-list-ol',
        title: 'Nummerierte Liste'
      },
      '|',
      {
        name: 'heading-1',
        action: SimpleMDE.toggleHeading1,
        className: 'fa fa-header',
        title: 'Überschrift'
      },
      {
        name: 'heading-2',
        action: SimpleMDE.toggleHeading2,
        className: 'fa fa-header fa-header-x fa-header-2',
        title: 'Unterüberschrift'
      },
      '|',
      {
        name: 'link',
        action: SimpleMDE.drawLink,
        className: 'fa fa-link',
        title: 'Link/Verweis'
      },
      {
        name: 'image',
        className: 'fa fa-picture-o',
        title: 'Bild'
      },
      '|',
      {
        name: 'preview',
        action: SimpleMDE.togglePreview,
        className: 'sg sg-preview no-disable',
        title: 'Vorschau'
      },
      {
        name: 'guide',
        action: '/stadt/markdown',
        className: 'fa fa-question-circle',
        title: 'Möglichkeiten der Textauszeichnung'
      }
    ]
  })

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

  const focusListener = on(codemirrorEvents, ['focus', 'blur'], () => {
    containerEl.classList.toggle('editor-container-active', editor.codemirror.hasFocus())
  })

  imageEditor.emitter.on('files:select', (files) => {
    const text = editor.codemirror.getSelection()
    const code = files.map((file) => {
      return `![${(text.length > 0) ? text : file.label}](${file.content})`
    }).join('\n')

    editor.codemirror.doc.replaceSelection(code)
    drop.close()
  })

  imageEditor.emitter.on('files:add', (files) => {
    files.forEach((file) => {
      form.appendChild(bel`<input type="hidden" name="images" value="${file.id}">`)
    })
  })

  const citeListener = bus.on(EVENT_CITE, data => {
    editor.codemirror.doc.replaceSelection(quote(data.formattedText))
  })

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
