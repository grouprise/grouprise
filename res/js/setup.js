import { $ } from 'luett'
import Vue from 'vue'

import Select from './core/components/select.vue'
import Avatar from './core/components/avatar.vue'
import NumberSpinner from './core/components/number-spinner.vue'
import Configurator from './core/components/configurator.vue'

Vue.component('sg-select', Select)
Vue.component('sg-avatar', Avatar)
Vue.component('sg-number-spinner', NumberSpinner)
Vue.component('sg-configurator', Configurator)

// load config
window.app = {
  conf: JSON.parse($('#app-configuration').textContent)
}
