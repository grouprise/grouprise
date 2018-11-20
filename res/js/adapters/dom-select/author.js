export default (gestaltApi, gestaltId, groupChoices) => {
  const gestaltQuery = gestaltApi.get(gestaltId).catch(() => null)

  const get = async choices => {
    const groups = await groupChoices.get(choices)
    const gestalt = await gestaltQuery
    const result = {choices: groups.choices}

    if (gestalt) {
      gestalt.value = ''
      gestalt.text = gestalt.name
      gestalt.label = gestalt.name
      result.defaultChoice = gestalt
    }

    return result
  }

  const texts = {
    ...groupChoices.texts,
    noSelection: 'Du selbst'
  }

  return {
    ...groupChoices,
    texts,
    get
  }
}
