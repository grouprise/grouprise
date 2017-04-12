import 'object-assign-shim'
import Promise from 'es6-promise'
import Vue from 'vue'
import { $ } from 'luett'

import Select from './core/components/select.vue'
import Avatar from './core/components/avatar.vue'
import DateTime from './core/components/datetime.vue'
import NumberSpinner from './core/components/number-spinner.vue'
import Switch from './core/components/switch.vue'
import Configurator from './core/components/configurator.vue'

// polyfills
Promise.polyfill()

// component registration
Vue.component('sg-select', Select)
Vue.component('sg-avatar', Avatar)
Vue.component('sg-datetime', DateTime)
Vue.component('sg-number-spinner', NumberSpinner)
Vue.component('sg-switch', Switch)
Vue.component('sg-configurator', Configurator)

// app configuration
window.app = {
  conf: JSON.parse($('#app-configuration').textContent)
}
