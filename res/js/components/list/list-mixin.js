export default {
  data () {
    return {
      objectList: [],
      nextPageURL: null
    }
  },
  methods: {
    load (url, objectList) {
      fetch(url, {credentials: 'same-origin'})
        .then(res => res.json())
        .then(paginator => {
          this.objectList = objectList.concat(paginator.results)
          this.nextPageURL = paginator.next
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
