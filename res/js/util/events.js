import EventEmitter from 'eventemitter3'

function evented (obj) {
  Object.assign(obj, EventEmitter.prototype)
  return obj
}

function eventedFunction (func) {
  function wrapper () {
    wrapper.emit('dispatch', arguments)
    const result = func.apply(this, arguments)
    wrapper.emit('call', result)
    return result
  }
  evented(wrapper)
  return wrapper
}

function SingletonListener (listenerFactory, callback) {
  const iface = {}
  const subscribers = []
  let listener

  function propagate (event) {
    subscribers.forEach(sub => callback.call(this, event, sub))
  }

  function init () {
    listener = listenerFactory(propagate)
  }

  iface.register = sub => {
    if (!listener) init()
    subscribers.push(sub)
    return iface
  }

  iface.remove = sub => {
    const index = subscribers.indexOf(sub)
    if (index > 0) {
      subscribers.splice(index, 1)
      if (subscribers.length === 0) {
        listener.destroy()
        listener = null
      }
    }
    return iface
  }

  return iface
}

export { evented, eventedFunction, SingletonListener }
