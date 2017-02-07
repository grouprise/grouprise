import decorator from './_decorator'
import { cookie } from 'cookie_js'

export default decorator((req, opts) => {
  const endpoint = opts.url(`gestalten/${window.app.conf.gestalt.id}/settings/`)

  const get = (params = {}) => {
    return req.get(endpoint, {params})
  }

  const create = (data = {}) => {
    const headers = {
      'X-CSRFToken': cookie.get('csrftoken')
    }

    return req.post(endpoint, data, { headers })
      .then(res => Promise.resolve(res.data))
  }

  return {get, create}
})
