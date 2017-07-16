import { includes, isPlainObject } from 'lodash'
import { cookie } from 'cookie_js'
import axios from 'axios'

const noop = config => config
const url = extension => `/stadt/api/${extension}`

function addToken (config) {
  const methods = ['post', 'put', 'patch', 'delete']
  const token = cookie.get('csrftoken', null)

  if (includes(methods, config.method) && isPlainObject(config.data) && token) {
    config.headers['X-CSRFToken'] = token
  }

  return config
}

export default handler => {
  return (req, opts = {}) => {
    let request

    if (!req) {
      request = axios.create()
      request.interceptors.request.use(addToken)
      request.interceptors.request.use(opts.modify || noop)
    }

    return handler(request, Object.assign({}, opts, { url }))
  }
}
