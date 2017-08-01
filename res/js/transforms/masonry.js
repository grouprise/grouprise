import Masonry from 'masonry-layout'
import imagesLoaded from 'imagesloaded'
import bel from 'bel'
import { defaults } from 'lodash'
import EffectRenderer, { amun } from './masonry.effects'

const classBase = 'masonry'
const classLoading = 'masonry-loading'

const selectorOrSize = value => /[0-9]+/.test(value) ? parseInt(value, 10) : value
const time = () => (new Date()).getTime()

export default function masonry (el, opts) {
  const gutterEl = bel`<li class='entity-list-gutter' role='presentation'></li>`
  const conf = defaults({}, opts.conf, {
    itemselector: 'li:not([role="presentation"])',
    columnwidth: 'li:not([role="presentation"])',
    gutter: '.entity-list-gutter',
    minimumLoadingTime: 500
  })

  el.appendChild(gutterEl)
  el.style.height = `${el.getBoundingClientRect().height}px`
  el.classList.add(classBase, classLoading)

  const timeStart = time()
  const effectRenderer = EffectRenderer(el)
  const msnry = new Masonry(el, {
    itemSelector: selectorOrSize(conf.itemselector),
    columnWidth: selectorOrSize(conf.columnwidth),
    gutter: selectorOrSize(conf.gutter),
    percentPosition: true,
    transitionDuration: 0,
    initLayout: false
  })
  const onLayoutComplete = () => {
    const waitTime = Math.max(0, conf.minimumLoadingTime - (time() - timeStart))
    setTimeout(() => {
      el.classList.remove(classLoading)
      effectRenderer.render(amun)
    }, waitTime)
  }
  const onImagesLoaded = () => {
    msnry.layout()
  }

  msnry.on('layoutComplete', onLayoutComplete)
  imagesLoaded(el, onImagesLoaded)

  return {
    remove () {
      effectRenderer.reset()
      msnry.off('layoutComplete', onLayoutComplete)
      msnry.destroy()
      el.removeChild(gutterEl)
      el.classList.remove(classBase, classLoading)
    }
  }
}
