import Vue from 'vue'
import {VueMasonryPlugin} from 'vue-masonry'
import GroupList from '../components/list/group-list.vue'

export default (el, opts) => {
  const state = {}

  Vue.use(VueMasonryPlugin)

  const vue = new Vue({
    el,
    data: state,
    render (h) {
      return h(GroupList, {
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
