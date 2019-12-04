import { $$, remove, getAttr, hasAttr, insertElement } from 'luett'
import { get } from 'lodash'
import Vue from 'vue'

import Adapters from '../adapters/dom-select'

const generateChoices = (defaultValue, option) => {
  const value = getAttr(option, 'value')
  return {
    value: value,
    text: option.textContent,
    label: getAttr(option, 'label', ''),
    isCurrent: hasAttr(option, 'selected'),
    isDefault: defaultValue === value
  }
}

export default (el, opts) => {
  const adapter = Adapters[opts.conf.type]
  let vue
  let container
  let data = $$('option', el).map(generateChoices.bind(null, opts.conf.defaultValue || ''))
  const defaultValue = data.reduce((result, option) => option.isDefault ? option.value : result, null)
  const value = data.reduce((result, option) => option.isCurrent ? option.value : result, null)
  const Select = Vue.component('sg-select')

  if (get(opts, 'skipDefault', true)) {
    data = data.filter(option => !option.isDefault)
  }

  adapter.get(data)
    .then(model => {
      container = document.createElement('div')
      container.id = `${el.id}-container`
      insertElement.after(el, container)
      el.style.display = 'none'

      vue = new Vue({
        el: `#${container.id}`,
        data: {
          model,
          defaultValue,
          value,
          adapter
        },
        render (h) {
          return h(Select, {
            props: {
              choices: this.model.choices,
              defaultChoice: this.model.defaultChoice,
              renderer: this.adapter.renderer,
              texts: this.adapter.texts,
              filter: this.adapter.filter,
              defaultValue: this.defaultValue,
              value: this.value
            },
            on: {
              input (value) {
                vue.value = value
                el.value = value
                el.dispatchEvent(new window.Event('change'))
              }
            }
          })
        }
      })
    })

  return {
    remove () {
      if (vue) vue.$destroy()
      if (container) remove(container)
    }
  }
}
