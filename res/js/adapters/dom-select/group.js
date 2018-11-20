import { find, includes } from 'lodash'
import ContentMeta from '../../components/content/content-meta.vue'

export default api => {
  const get = choices => {
    const ids = choices.map(option => option.value).join(',')

    return api.list({id: ids})
      .then(response => response.data)
      .then(data =>
        choices.map(choice => ({
          ...choice,
          ...find(data, entity => entity.id === parseInt(choice.value, 10))
        }))
      )
      .then(choices => ({choices, defaultChoice: null}))
  }

  const filter = (term, choice, defaultFilter) => {
    return defaultFilter(term, choice) ||
      (choice.tags || []).reduce((result, tag) => result || includes(tag.name.toLowerCase(), term), false)
  }

  const texts = {
    searchPlaceholder: 'Suche Gruppennamen, z.B. stadt',
    searchLabel: 'Suche Gruppen',
    noResult: 'Keine Gruppen gefunden 😔',
    noSelection: 'Keine Gruppe gewählt'
  }

  return {texts, filter, get, renderer: ContentMeta}
}
