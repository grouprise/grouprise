import { find, matches } from 'lodash'

export default (gestaltApi, gestaltId, groupAdapter) => {
  const gestalten = gestaltApi.get()
    .then(response => Promise.resolve(response.data), () => null)

  const get = choices => {
    return Promise.all([groupAdapter.get(choices), gestalten])
      .then(data => {
        const [groups, gestalten] = data
        const result = {choices: groups.choices}
        const gestalt = find(gestalten, matches({id: gestaltId}))

        if (gestalt) {
          gestalt.value = ''
          gestalt.text = gestalt.name
          gestalt.label = gestalt.name
          result.defaultChoice = gestalt
        }

        return Promise.resolve(result)
      })
  }

  const texts = Object.assign({}, groupAdapter.texts, {
    noSelection: 'Du selbst'
  })

  return Object.assign({}, groupAdapter, {texts, get})
}
