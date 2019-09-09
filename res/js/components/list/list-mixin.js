import { danger } from '../../util/notify'

export default {
  data () {
    return {
      objectList: [],
      nextPageURL: null,
      loading: false
    }
  },
  methods: {
    load (url, objectList) {
      this.loading = true
      fetch(url, {credentials: 'same-origin'})
        .then(res => res.json())
        .then(paginator => {
          this.objectList = objectList.concat(paginator.results)
          this.nextPageURL = paginator.next
          this.loading = false
        })
        .catch(error => {
          this.loading = false
          danger('Fehler bei der Kommunikation mit dem Server')
        })
    },
    loadMore () {
      this.load(this.nextPageURL, this.objectList)
    },
    loadInitial (baseURL) {
      // reload object list with filter params
      let params = new URLSearchParams()
      Object.entries(this.filters).forEach(([k, v]) => params.set(k, v))
      this.load(baseURL + params, [])
    }
  }
}
