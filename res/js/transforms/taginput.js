import Tagify from '@yaireo/tagify'

export default (el, opts) => {
  const list = el.getAttribute('list')
  const listEl = list ? document.getElementById(list) : null
  const suggestions = listEl ? Array.from(listEl.children).map(el => el.textContent) : []
  const tagify = new Tagify(el, {
    whitelist: suggestions,
    delimiters: ',',
    dropdown: {
      enabled: 0,
    },
    originalInputValueFormat (values) {
      return values.map(({value}) => value).join(',')
    }
  })

  return {
    destroy () {
      tagify.destroy()
    }
  }
}
