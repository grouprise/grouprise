import decorator from './_decorator'

export default decorator((req, opts) => {
  const endpoint = opts.url('groups/')

  const get = (params = {}) => {
    return req.get(endpoint, {params})
  }

  const single = (id) => {
    return req.get(`${endpoint}${id}/`)
      .then(res => res.data)
  }

  return {get, single}
})
