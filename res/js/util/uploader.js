import { sum } from 'lodash'

function progressAdapterFactory(callback) {
  const iface = {}
  const handlers = []

  function propagateProgress() {
    const progress = sum(handlers) / handlers.length
    callback({
      complete: Math.max(0, Math.min(100, progress)),
      jobCount: handlers.length
    })
  }

  iface.createHandler = () => {
    const id = handlers.length
    handlers[id] = 0
    return progress => {
      if(progress.lengthComputable) {
        handlers[id] = progress.loaded / progress.total * 100
        propagateProgress()
      }
    }
  }

  return iface
}

export default function UploaderFactory (adapter) {
  function upload (files, onProgress) {
    const progressAdapter = progressAdapterFactory(onProgress)
    const uploads = files.map(file => {
      return adapter.create({file}, {onProgress: progressAdapter.createHandler()})
    })
    return Promise.all(uploads)
  }

  return { upload }
}

