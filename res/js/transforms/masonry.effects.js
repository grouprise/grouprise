import { $$ } from 'luett'
import anime from 'animejs'

export const amun = {
  sortTargetsFn: (a, b) => {
    const aBounds = a.getBoundingClientRect()
    const bBounds = b.getBoundingClientRect()

    return (aBounds.left - bBounds.left) || (aBounds.top - bBounds.top)
  },
  animeOpts: {
    duration: (t, i) => 500 + i * 50,
    easing: 'easeOutExpo',
    delay: (t, i) => i * 20,
    opacity: {
      value: [0, 1],
      duration: (t, i) => 250 + i * 50,
      easing: 'linear'
    },
    translateY: [400, 0]
  }
}

export default function EffectRenderer (masonry) {
  const items = $$("li:not([role='presentation']) > :first-child", masonry)

  const reset = () => {
    items.forEach(item => {
      item.style.removeProperty('opacity')
      item.style.removeProperty('transformOrigin')
      item.style.removeProperty('transform')
      item.parentNode.style.removeProperty('overflow')
    })
  }

  const render = effect => {
    reset()

    const { animeOpts } = effect
    animeOpts.targets = typeof effect.sortTargetsFn === 'function'
      ? items.sort(effect.sortTargetsFn)
      : items
    anime.remove(animeOpts.targets)
    anime(animeOpts)
  }

  return { reset, render }
}
