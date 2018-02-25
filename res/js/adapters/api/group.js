import decorator from './_decorator'

export default decorator((req, opts) => {
  const endpoint = opts.url('groups/')

  const list = (params = {}, options = {}) => {
    return req.get(endpoint, {params, ...options})
  }

  const get = id => {
    return req.get(`${endpoint}${id}/`)
      .then(res => res.data)
  }

  return {list, get}
})
