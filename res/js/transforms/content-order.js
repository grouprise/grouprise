import Vue from 'vue'
import { $ } from 'luett'
import { selectAdapter, valueSubmissionAdapter } from '../adapters/dom'
import { createContainerAdapter } from '../util/dom'
import ContentOrder from '../components/content/content-order.vue'

export default el => {
  const filterEl = $('select', el)
  const submitEl = $('button', el)
  const filter = valueSubmissionAdapter(selectAdapter(filterEl), submitEl)
  const state = {
    order: filter.get().value
  }

  const containerAdapter = createContainerAdapter(el)
  const vue = new Vue({
    el: `#${containerAdapter.container.id}`,
    data: state,
    render (h) {
      return h(ContentOrder, {
        props: {
          value: this.order
        },
        on: {
          input (value) {
            filter.set({ value })
          }
        }
      })
    }
  })
  containerAdapter.replacedEl.hide()

  return {
    remove () {
      vue.$destroy()
      containerAdapter.replacedEl.show()
      containerAdapter.destroy()
    }
  }
}
