/**
 * @param {HTMLElement} el
 * @returns {{destroy(): void}|*}
 */
export default (el) => {
  function updateScrollData () {
    el.style.setProperty('--scroll-container-offset-x', el.scrollLeft)
    el.style.setProperty('--scroll-container-offset-y', el.scrollTop)
    el.style.setProperty('--scroll-container-scroll-width', el.scrollWidth)
    el.style.setProperty('--scroll-container-scroll-height', el.scrollHeight)
    el.style.setProperty('--scroll-container-width', el.clientWidth)
    el.style.setProperty('--scroll-container-height', el.clientHeight)
  }

  el.addEventListener('scroll', updateScrollData, { passive: true })
  updateScrollData()

  return {
    destroy () {
      el.removeEventListener('scroll', updateScrollData)
    }
  }
}
