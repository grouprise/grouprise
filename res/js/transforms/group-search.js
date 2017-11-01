import Vue from 'vue'
import GroupSearch from '../components/content/group-search.vue'

export default el => {
  const defaultResults = el.innerHTML
  const vue = new Vue({
    el: el,
    render (h) {
      return h(GroupSearch, {
        props: {
          defaultResults
        }
      })
    }
  })

  return {
    vue,
    remove () {
      vue.$destroy()
    }
  }
}
