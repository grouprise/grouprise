import { chain, each, has, pick } from 'lodash'
import { cookie } from 'cookie_js'
import decorator from './_decorator'

const numberOrNull = numeric => {
  const num = parseInt(numeric, 10)
  return isNaN(num) ? null : num
}

const dropInvalid = value => !!value

const normalizer = {
  id: numberOrNull,
  weight: numberOrNull,
  content: numberOrNull
}

const filter = {
  id: dropInvalid,
  content: dropInvalid
}

const imageDefaults = data => {
  return chain(data)
    .defaults({
      weight: 0,
      csrfmiddlewaretoken: cookie.get('csrftoken')
    })
    .mapKeys((value, key) => ({
      contentId: 'content'
    }[key] || key))
    .mapValues((value, key) => has(normalizer, key) ? normalizer[key](value) : value)
    .pickBy((value, key) => has(filter, key) ? filter[key](value) : true)
    .value()
}

const transform = file => ({
  id: file.id,
  label: file.title,
  content: file.path
})

export default decorator((req, opts) => {
  const endpoint = opts.url('images/')

  const get = (params = {}) => {
    return req.get(endpoint, {params})
      .then(res => Promise.resolve(res.data.map(transform)))
  }

  const create = (data = {}) => {
    const formData = new window.FormData()
    each(imageDefaults(data), (value, key) => formData.append(key, value))

    return req.post(endpoint, formData)
      .then(res => Promise.resolve(transform(res.data)))
  }

  const update = (data = {}) => {
    const putData = imageDefaults(pick(data, ['id', 'weight']))
    return req.put(endpoint, putData)
      .then(res => Promise.resolve(res.data))
  }

  return {get, create, update}
})
