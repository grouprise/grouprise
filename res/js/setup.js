import { $ } from 'luett'
import Vue from 'vue'

import Select from './core/components/select.vue'
import Avatar from './core/components/avatar.vue'

Vue.component('sg-select', Select)
Vue.component('sg-avatar', Avatar)

// load config
window.app = {
  conf: JSON.parse($('#app-configuration').textContent)
}
