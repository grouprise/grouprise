import { sum, isFunction } from 'lodash'
import Q from 'q'

function progressAdapterFactory (onProgressCallback) {
  const iface = {}
  const handlers = []

  function propagateProgress () {
    const progress = sum(handlers) / handlers.length
    onProgressCallback({
      complete: Math.max(0, Math.min(100, progress)),
      jobCount: handlers.length
    })
  }

  iface.createHandler = () => {
    const id = handlers.length
    handlers[id] = 0
    return progress => {
      if (progress.lengthComputable) {
        handlers[id] = progress.loaded / progress.total * 100
        propagateProgress()
      }
    }
  }

  return iface
}

function selectResolver (spec) {
  switch (true) {
    case spec === 'all':
      return Q.all
    case spec === 'allSettled':
      return Q.allSettled
    case isFunction(spec):
      return spec
    default:
      throw Error('unknown resolver', spec)
  }
}

export default function UploaderFactory (adapter) {
  function upload (files, onProgress, resolveWith = 'all') {
    const resolver = selectResolver(resolveWith)
    const progressAdapter = progressAdapterFactory(onProgress)
    const uploads = files.map(file => {
      return adapter.create({file}, {onProgress: progressAdapter.createHandler()})
    })
    return resolver(uploads)
  }

  return { upload }
}
