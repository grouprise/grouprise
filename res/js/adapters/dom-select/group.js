import { find, includes } from 'lodash'
import ContentMeta from '../../content/components/content-meta.vue';

export default api => {
  const get = choices => {
    const ids = choices.map(option => option.value).join(',')

    return api.get({id: ids})
      .then(response => Promise.resolve(response.data))
      .then(data => Promise.resolve(choices.map(choice => {
        return Object.assign({}, choice, find(data, entity => entity.id === parseInt(choice.value, 10)))
      })))
      .then(choices => Promise.resolve({ choices, defaultChoice: null }))
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
