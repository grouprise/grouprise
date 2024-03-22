import { createContainerAdapter } from 'app/util/dom'
import Vue from 'vue'
import PointsOfInterest from '../components/geo/PointsOfInterest.vue'

const KNOWN_LOADERS = ["group"]

function loadPointsOfInterestFromAPI(apiLoaderQuery) {
  const [apiName, queryString] = apiLoaderQuery.split('?')
  if (!KNOWN_LOADERS.includes(apiName)) {
    throw new Error(`Unknown POI Loader ${apiName}`)
  }
  const queryParams = queryString ? Object.fromEntries(new URLSearchParams(queryString)) : {}
  // endpoints should support the common location API filters and include directive
  queryParams['has_location'] = 'True'
  queryParams['include'] = queryParams['include'] || '' + ',location'
  return import('../adapters/api')
    .then(m => m[apiName])
    .then(api => api.list(queryParams))
    .then(res => res.data)
    .then(data => {
      return data.map((object, index) => {
        const location = object.location
        delete object.location
        return {
          id: index,
          source: apiName,
          location,
          object
        }
      })
    })
}

export default (el, { conf }) => {
  const containerAdapter = createContainerAdapter(el, 'child')
  const state = {
    pointsOfInterest: el.textContent.trim()
      ? JSON.parse(el.textContent)
      : []
  }

  if (conf.apiLoaderQuery) {
    loadPointsOfInterestFromAPI(conf.apiLoaderQuery)
      .then(pois => {
        state.pointsOfInterest = pois
      })
  }

  const vue = new Vue({
    el: `#${containerAdapter.container.id}`,
    data: state,
    render (h) {
      return h(PointsOfInterest, {
        props: {
          pointsOfInterest: this.pointsOfInterest,
          height: conf.height,
          restrictView: conf.restrictView,
        }
      })
    }
  })

  return {
    remove () {
      vue.$destroy()
      containerAdapter.replacedEl.show()
      containerAdapter.destroy()
    }
  }
}
