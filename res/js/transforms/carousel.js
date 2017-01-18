import { $, $$, getAttr } from 'luett'
import delegate from 'delegate'
import { range } from 'lodash'
import stroll from 'stroll.js'

function createScroller (el) {
  return stroll.factory(el)
}

function attachNav (el, opts) {
  el.insertAdjacentHTML('beforeend', `
        <div class="${opts.cssNav}">
            <div>
                <button type="button" class="${opts.cssNavBtn} ${opts.cssNavBtnPrev}">
                    <i class="${opts.cssNavBtnIcon}"></i>
                </button>            
            </div>
            <div>
                <button type="button" class="${opts.cssNavBtn} ${opts.cssNavBtnNext}">
                    <i class="${opts.cssNavBtnIcon}"></i>
                </button>
            </div>
        </div>
    `)
}

function attachIndex (el, opts, numberOfSlides) {
  if (numberOfSlides <= 1) {
    return
  }

  el.insertAdjacentHTML('beforeend', `
        <ol class="${opts.cssIndex}">
            ${range(1, Math.min(numberOfSlides + 1, 5)).map(idx => `
                <li>
                    <button type="button" class="${opts.cssIndexBtn}" data-carousel-index="${idx}"></button>
                </li>
            `).join('\n')}
        </ol>
    `)
}

function carousel (root, options) {
  const conf = Object.assign({}, carousel.DEFAULTS, options.conf)
  const iface = Object.create(null)
  const crsl = $(`.${conf.cssCarousel}`, root)

    // create a default scroller
  let scroller = createScroller(crsl)
    // configure noop emitter
  let emit = () => {}

    // set state
  let currentSlide = 1

  function unsetCurrent () {
    $$(`.${conf.cssSlides} > .${conf.cssCurrent}`, root)
            .forEach((item) => item.classList.remove(conf.cssCurrent))
  }

  function setCurrent (el) {
    el.classList.add(conf.cssCurrent)
    return scroller({ x: el.offsetLeft, y: el.offsetTop })
  }

  function showSlide (idx) {
    const slide = $(`.${conf.cssSlides} > :nth-child(${idx})`, root)

    if (!slide) return iface

    root.classList.toggle(conf.cssSlidesFirst, idx === 1)
    root.classList.toggle(conf.cssSlidesLast, idx === getNumberOfSlides())

    const eventData = { index: idx, carousel: crsl, slide }

    emit('slide:start', eventData)
    unsetCurrent()
    setCurrent(slide)
            .then(function () {
              emit('slide:end', eventData)
            })

    currentSlide = idx

    return iface
  }

  function getNumberOfSlides () {
    return $(`.${conf.cssSlides}`).children.length
  }

  iface.setEmitter = (emitter) => {
    emit = emitter
    return iface
  }

  iface.setScroller = (factory) => {
    scroller = factory(crsl)
    return iface
  }

  iface.showSlide = (idx) => {
    return showSlide(idx)
  }

  iface.nextSlide = () => {
    return showSlide(currentSlide + 1)
  }

  iface.prevSlide = () => {
    return showSlide(currentSlide - 1)
  }

  delegate(root, `.${conf.cssNavBtn}`, 'click', function (event) {
    event.preventDefault()

    if (event.delegateTarget.classList.contains(conf.cssNavBtnPrev)) {
      iface.prevSlide()
    }

    if (event.delegateTarget.classList.contains(conf.cssNavBtnNext)) {
      iface.nextSlide()
    }
  })

  delegate(root, `.${conf.cssIndexBtn}`, 'click', function (event) {
    event.preventDefault()
    const idx = parseInt(getAttr(event.delegateTarget, 'data-carousel-index'), 10)
    showSlide(idx)
  })

    // add nav
  attachNav(root, conf)
  attachIndex(root, conf, getNumberOfSlides())

    // set first slide as current but wait for carousel to return
  setTimeout(() => iface.showSlide(currentSlide), 0)

  return iface
}

carousel.DEFAULTS = {
  cssCurrent: 'carousel-current',
  cssSlides: 'carousel-slides',
  cssSlidesFirst: 'carousel-first',
  cssSlidesLast: 'carousel-last',
  cssNav: 'carousel-nav',
  cssNavBtn: 'carousel-btn',
  cssNavBtnIcon: 'carousel-btn-icon',
  cssNavBtnPrev: 'carousel-btn-prev',
  cssNavBtnNext: 'carousel-btn-next',
  cssCarousel: 'carousel',
  cssIndex: 'carousel-index',
  cssIndexBtn: 'carousel-btn-index'
}

export default carousel
