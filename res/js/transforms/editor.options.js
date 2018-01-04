import { markdown } from '../adapters/api'

function showPreview (plainText, preview) {
  const onSuccess = content => {
    preview.innerHTML = `<div class="content-body">${content}</div>`
  }
  const onFailure = () => {
    preview.innerHTML = `<p class="disclaimer">Fehler beim Laden der Vorschau</p>`
  }

  markdown.parse(plainText).then(onSuccess, onFailure)

  // return loading indication while processing request
  return 'Lade Vorschau...'
}

export default (el, SimpleMDE) => ({
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
  previewRender: showPreview,
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
