import { throttle } from 'lodash'
import { $, matchesMedia, on, attr } from 'luett'

const forAttr = attr('for')
const dataOpenableTargetAttr = attr('data-openable-target')

export default el => {
  const dockContent = $('.dock-content', el)
  const dockHeader = $('.dock-header', el)
  const switchState = $('#' + forAttr.get(dataOpenableTargetAttr.$('#' + el.id)))

  const setHeight = matchesMedia.max.small(
    () => {
      if (switchState.checked) {
        setTimeout(() => {
          const windowHeight = window.innerHeight
          const dockHeaderSize = dockHeader.getBoundingClientRect().height
          dockContent.style.maxHeight = `calc(${windowHeight}px - 120px - 2px - 2rem - .75rem - ${dockHeaderSize}px)`
        }, 250)
      }
    },
    () => {
      dockContent.style.maxHeight = null
    }
  )

  const switchListener = on(switchState, 'change', setHeight)
  const scrollListener = on(dockContent, 'scroll', throttle(() => {
    el.classList.toggle('dock-content-scrolled', dockContent.scrollTop > 2)
  }, 100), { passive: true })
  setHeight()

  return {
    destroy () {
      switchListener.destroy()
      scrollListener.destroy()
    }
  }
}
