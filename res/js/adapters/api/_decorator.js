import axios from 'axios'

const noop = config => config
const url = extension => `/stadt/api/${extension}`

export default handler => {
  return (req, opts = {}) => {
    let request

    if (!req) {
      request = axios.create()
      request.interceptors.request.use(opts.modify || noop)
    }

    return handler(request, Object.assign({}, opts, { url }))
  }
}
