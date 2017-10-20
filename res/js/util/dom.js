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

export function getTimeFormat (date) {
  // todo there might be a better way to do this :)
  // detect the date-format based on the current value
  for (const [check, format] of getTimeFormat.formats) {
    if (check.test(date.value)) {
      getTimeFormat.default = format
      return format
    }
  }

  console.error(`unknown timeformat for date ${date.value}`)
  return getTimeFormat.default
}

getTimeFormat.formats = [
  [/^[\d]{4}-[\d]{2}-[\d]{2}/, 'YYYY-MM-DD HH:mm:ss'],
  [/^[\d]{2}\.[\d]{2}\.[\d]{4}/, 'DD.MM.YYYY HH:mm:ss']
]
getTimeFormat.default = getTimeFormat.formats[0][1]
getTimeFormat.toString = () => getTimeFormat.default

export default {
  createDisplayControl,
  createContainerAdapter,
  getTimeFormat
}
