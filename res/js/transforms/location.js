import { $ } from 'luett'
import { createContainerAdapter } from 'app/util/dom'
import Vue from 'vue'
import Location from '../components/geo/Location.vue'

export default (el, { conf }) => {
  const $input = $('[data-location-input]', el)
  const $selection = $('[data-location-selection]', el)
  const containerAdapter = createContainerAdapter($selection)
  const state = {
    location: $input.value
  }

  const vue = new Vue({
    el: `#${containerAdapter.container.id}`,
    data: state,
    created () {
      containerAdapter.replacedEl.hide()
    },
    render (h) {
      return h('div', [
        h(Location, {
          props: {
            point: this.location,
            help: conf.help
          },
          on: {
            input (value) {
              $input.value = state.location = value
            }
          }
        }),
        h('div', { class: 'help-block', domProps: { innerHTML: conf.help } }),
      ])
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
