import Vue from 'vue'
import GroupList from '../components/list/group-list.vue'

export default (el, opts) => {
  const state = {}

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
