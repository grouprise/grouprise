import randomId from 'random-id'
import { remove, insertElement } from 'luett'

export function createDisplayControl (...args) {
  function doWithArgs (callback) {
    for (const arg of args) {
      if (arg) {
        callback(arg)
      }
    }
  }

  return {
    show: () => {
      doWithArgs(el => { delete el.style.display })
    },
    hide: () => {
      doWithArgs(el => { el.style.display = 'none' })
    }
  }
}

export function createContainerAdapter (el) {
  const id = el.id || randomId(20, 'a')
  const containerWrapper = document.createElement('div')
  containerWrapper.id = `${id}-container-wrapper`
  const container = document.createElement('div')
  container.id = `${id}-container`
  containerWrapper.appendChild(container)
  insertElement.after(el, containerWrapper)

  return {
    container,
    replacedEl: createDisplayControl(el),
    destroy: () => { remove(containerWrapper) }
  }
}

export default {
  createDisplayControl,
  createContainerAdapter
}
