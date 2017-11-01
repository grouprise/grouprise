import decorator from './_decorator'

export default decorator((req, opts) => {
  const endpoint = opts.url('groups/')

  const get = (params = {}, options = {}) => {
    return req.get(endpoint, {params, ...options})
  }

  const single = (id) => {
    return req.get(`${endpoint}${id}/`)
      .then(res => res.data)
  }

  return {get, single}
})
