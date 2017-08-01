import { get, filter, stubFalse } from 'lodash'
import { on } from 'luett'

function HistoryStateDispatcher () {
  const handlers = {}
  const iface = {}
  let popstateListener

  function register (name, callback, acceptFilter = stubFalse) {
    const iface = {}
    handlers[name] = callback
    callback.accepts = acceptFilter

    iface.pushState = (state, title, url) => {
      window.history.pushState({ handler: name, payload: state }, title, url)
      return iface
    }

    iface.destroy = () => {
      delete handlers[name]
    }

    return iface
  }

  function dispatch (event) {
    const handler = get(event, 'state.handler')

    if (handlers[handler]) {
      handlers[handler](event.state.payload, event)
      return
    }

    {
      let wasCalled = false
      filter(handlers, handler => handler.accepts(event))
        .forEach(handler => {
          wasCalled = true
          handler(event.state, event)
        })

      if (wasCalled) return
    }

    console.debug('discarding popstate event', event)
  }

  function mount () {
    if (popstateListener) return iface
    popstateListener = on(window, 'popstate', dispatch)
    return iface
  }

  function destroy () {
    if (popstateListener) {
      popstateListener.destroy()
    }
  }

  Object.assign(iface, { register, mount, destroy })

  return iface
}

export default HistoryStateDispatcher
