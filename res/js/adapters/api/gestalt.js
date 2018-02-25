import decorator from './_decorator'

export default decorator((req, opts) => {
  const endpoint = opts.url('gestalten/')

  const list = (params = {}) => {
    return req.get(endpoint, {params})
  }

  const get = id => {
    return req.get(`${endpoint}${id}/`)
      .then(res => res.data)
  }

  return {list, get}
})
