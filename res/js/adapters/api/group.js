import decorator from './_decorator'

export default decorator((req, opts) => {
  const endpoint = opts.url('groups/')

  const get = (params = {}) => {
    return req.get(endpoint, {params})
  }

  return {get}
})
