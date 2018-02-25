import delegate from 'delegate'
import { keyPressed, $, matchesMedia, on, attr } from 'luett'
import { fromPairs, mapValues, includes } from 'lodash'

const menuGroupAttr = attr('data-menu-group')
const body = $('body')

function createSearch (el) {
  const searchState = $('[data-search-state]', el)
  const searchInput = $('[data-search-input]', el)

  const stateListener = on(searchState, 'change', () => {
    if (searchState.checked) {
      searchInput.focus()
    }
  })

  return {
    destroy () {
      stateListener.destroy()
    }
  }
}

export default el => {
  const search = createSearch(el)
  const switchState = $('[data-menu-switch]', el)
  const firstSubMenu = menuGroupAttr.$(el)
  const states = fromPairs(menuGroupAttr.$$(el).map(i => [i.id, i]))
  const stateLabels = mapValues(states, i => $(`[for='${i.id}']`, el))
  let triggerTimeout

  const keydownListener = delegate(el, 'label', 'keydown', keyPressed(13, e => {
    if (includes(stateLabels, e.delegateTarget)) {
      e.delegateTarget.click()
    }
  }))

  const switchListener = on(switchState, 'change', matchesMedia.max.small(e => {
    body.style.overflow = switchState.checked ? 'hidden' : null
    if (switchState.checked && firstSubMenu) {
      clearTimeout(triggerTimeout)
      triggerTimeout = setTimeout(() => { stateLabels[firstSubMenu.id].click() }, 200)
    }
  }))
  body.style.overflow = switchState.checked ? 'hidden' : null

  return {
    remove () {
      keydownListener.destroy()
      switchListener.destroy()
      search.destroy()
    }
  }
}
