import decorator from './_decorator'

export default decorator((req, opts) => {
  const endpoint = opts.url(`gestalten/${window.app.conf.gestalt.id}/settings/`)

  const get = (params = {}) => {
    return req.get(endpoint, {params})
  }

  const create = (data = {}) => {
    return req.post(endpoint, data)
      .then(res => Promise.resolve(res.data))
  }

  return {get, create}
})
