import Vue from 'vue'
import ContentList from '../components/list/content-list.vue'

export default (el, opts) => {
  const state = {}

  const vue = new Vue({
    el,
    data: state,
    render (h) {
      return h(ContentList, {
        props: {}
      })
    }
  })

  return {
    remove () {
      vue.$destroy()
    }
  }
}
