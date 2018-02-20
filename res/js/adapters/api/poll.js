import decorator from './_decorator'

export default decorator((req, opts) => {
  const endpoint = opts.url('polls')

  const get = id => {
    return req.get(`${endpoint}/${id}/`)
      .then(res => res.data)
  }

  const vote = (id, data) => {
    return req.post(`${endpoint}/${id}/vote`, data)
      .then(res => res.data)
  }

  return {get, vote}
})
