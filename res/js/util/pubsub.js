import EventEmitter from 'eventemitter3'

function PubSub () {
  const emitter = new EventEmitter()
  const iface = {}

  iface.on = (event, callback, context) => {
    emitter.on(event, callback, context)
    return {
      destroy () {
        emitter.off(event, callback, context)
      }
    }
  }

  iface.emit = (event, data) => {
    emitter.emit(event, data)
    return iface
  }

  return iface
}

export default PubSub
