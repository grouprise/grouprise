import { each, has, pick, defaults, mapKeys, mapValues, pickBy } from 'lodash'
import cookie from 'cookie_js'
import decorator from './_decorator'

const numberOrNull = numeric => {
  const num = parseInt(numeric, 10)
  return isNaN(num) ? null : num
}

const dropInvalid = value => !!value

const normalizer = {
  id: numberOrNull
}

const filter = {
  id: dropInvalid
}

const imageDefaults = data => {
  return pickBy(
      mapValues(
        mapKeys(
          defaults(data, {
            creator: window.app.conf.gestalt.id,
            csrfmiddlewaretoken: cookie.get('csrftoken')
          }),
          (value, key) => ({ contentId: 'content' }[key] || key)
        ),
        (value, key) => has(normalizer, key) ? normalizer[key](value) : value
      ),
      (value, key) => has(filter, key) ? filter[key](value) : true
    )
}

const transform = file => ({
  id: file.id,
  label: file.title,
  content: file.path,
  preview: file.preview
})

export default decorator((req, opts) => {
  const endpoint = opts.url('images/')

  const get = (params = {}) => {
    return req.get(endpoint, {params})
      .then(res => Promise.resolve(res.data.map(transform)))
  }

  const create = (data = {}, conf = {}) => {
    const formData = new window.FormData()
    const requestConf = {}
    each(imageDefaults(data), (value, key) => formData.append(key, value))

    if (conf.onProgress) {
      requestConf.onUploadProgress = conf.onProgress
    }

    return req.post(endpoint, formData, requestConf)
      .then(res => Promise.resolve(transform(res.data)))
  }

  const update = (data = {}) => {
    const putData = imageDefaults(pick(data, ['id']))
    return req.put(endpoint, putData)
      .then(res => Promise.resolve(res.data))
  }

  return {get, create, update}
})
