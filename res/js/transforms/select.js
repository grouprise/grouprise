import { $$, remove, getAttr, hasAttr } from 'luett'
import { get } from 'lodash'
import Vue from 'vue'

import Adapters from '../adapters/dom-select'

const insert = (position, node, newNode) => {
  switch (position) {
    case 'beforebegin':
      node.parentNode.insertBefore(newNode, node)
      break
    case 'afterend':
      node.parentNode.insertBefore(newNode, node.nextElementSibling)
      break
  }
}

const insertAfter = insert.bind(null, 'afterend')
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

  if (get(opts, 'skipDefault', true)) {
    data = data.filter(option => !option.isDefault)
  }

  adapter.get(data)
    .then(model => {
      container = document.createElement('div')
      container.id = `${el.id}-container`
      insertAfter(el, container)
      el.style.display = 'none'

      vue = new Vue({
        template: `<sg-select :choices="model.choices" :defaultChoice="model.defaultChoice" 
                              :renderer="adapter.renderer" :texts="adapter.texts" :filter="adapter.filter" 
                              :defaultValue="defaultValue" v-model="value"></sg-select>`,
        el: `#${container.id}`,
        data: {
          model,
          defaultValue,
          value,
          adapter
        },
        watch: {
          value (value) {
            el.value = value
            el.dispatchEvent(new window.Event('change'))
          }
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
