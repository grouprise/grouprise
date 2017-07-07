import decorator from './_decorator'

export default decorator((req, opts) => {
  const endpoint = opts.url('content/markdown/')

  const parse = (content, prefix = 'content') => {
    return req.post(endpoint, { content, prefix })
      .then(res => Promise.resolve(res.data.content))
  }

  return {parse}
})
