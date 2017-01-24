import { $, $$, mapCall, getAttr, index } from 'luett'
import bel from 'bel'
import delegate from 'delegate'

import Photoswipe from 'photoswipe'
import theme from 'photoswipe/dist/photoswipe-ui-default'

function attachTemplate () {
  const template = bel`
<div class="pswp" tabindex="-1" role="dialog" aria-hidden="true">
    <div class="pswp__bg"></div>
    <div class="pswp__scroll-wrap">
        <div class="pswp__container">
            <div class="pswp__item"></div>
            <div class="pswp__item"></div>
            <div class="pswp__item"></div>
        </div>
        <div class="pswp__ui pswp__ui--hidden">
            <div class="pswp__top-bar">
                <div class="pswp__counter"></div>
                
                <button class="pswp__button pswp__button--close sg sg-close" title="Schließen (Esc)"></button>
                <button class="pswp__button pswp__button--share sg sg-share" title="Teilen"></button>
                <button class="pswp__button pswp__button--fs sg sg-fullscreen" title="Vollbild umschalten"></button>
                <button class="pswp__button pswp__button--zoom sg sg-zoom" title="Rein/Raus Zoomen"></button>
                
                <div class="pswp__preloader">
                    <div class="pswp__preloader__icn">
                      <div class="pswp__preloader__cut">
                        <div class="pswp__preloader__donut"></div>
                      </div>
                    </div>
                </div>
            </div>
            
            <div class="pswp__share-modal pswp__share-modal--hidden pswp__single-tap">
                <div class="pswp__share-tooltip"></div> 
            </div>
            
            <button class="pswp__button pswp__button--arrow--left sg sg-left" title="Vorheriges Bild"></button>
            <button class="pswp__button pswp__button--arrow--right sg sg-right" title="Nächstes Bild"></button>
            
            <div class="pswp__caption">
                <div class="pswp__caption__center"></div>
            </div>
        </div>
    </div>
</div>`

  document.body.appendChild(template)
  return template
}

function calculateBounding (images, index) {
  const image = images[index]
  const pageYScroll = window.pageYOffset || document.documentElement.scrollTop
  const rect = image.getBoundingClientRect()

  return {
    x: rect.left,
    y: rect.top + pageYScroll,
    w: rect.width
  }
}

function createLightbox (gallery) {
  const imageSelector = '[href]'
  const imageElements = $$(imageSelector, gallery)
  const images = mapCall(imageElements, (el) => {
    const [ w, h ] = mapCall(getAttr(el, 'data-size').split('x'), parseInt)
    return {
      msrc: getAttr($('img', el), 'src'),
      src: getAttr(el, 'href'),
      w,
      h
    }
  })

  function show (startWithIndex = 0) {
    const template = attachTemplate()
    const lightbox = new Photoswipe(template, theme, images, {
      index: startWithIndex,
      getThumbBoundsFn: calculateBounding.bind(null, imageElements),
      shareEl: false
    })

    lightbox.listen('destroy', function () {
      document.body.removeChild(template)
    })

    lightbox.init()
  }

  const destroyClickListener = delegate(gallery, imageSelector, 'click', function (e) {
    e.preventDefault()
    const targetIndex = index(e.delegateTarget.parentNode)
    show(targetIndex - 1)
  })

  return {
    show: show,
    remove: () => {
      destroyClickListener()
    }
  }
}

export default (el) => {
  return createLightbox($('.gallery', el))
}
