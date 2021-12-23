/* eslint-disable vue/component-definition-name-casing */
import Vue from 'vue'

// custom global vue filters
import { fallback, truncatewords } from './components/core/filters.js'

// vue setup
Vue.filter('default', fallback)
Vue.filter('truncatewords', truncatewords)
/* eslint-disable-next-line vue/multi-word-component-names */
Vue.component('draggable', () => import('vuedraggable'))
Vue.component('sg-file-picker', () => import('./components/core/file-picker.vue'))
Vue.component('sg-image-picker', () => import('./components/image/image-picker.vue'))
Vue.component('sg-input', () => import('./components/core/input.vue'))
Vue.component('sg-select', () => import('./components/core/select.vue'))
Vue.component('sg-avatar', () => import('./components/core/avatar.vue'))
Vue.component('sg-datetime', () => import('./components/time/datetime.vue'))
Vue.component('sg-number-spinner', () => import('./components/core/number-spinner.vue'))
Vue.component('sg-switch', () => import('./components/core/switch.vue'))
Vue.component('sg-configurator', () => import('./components/core/configurator.vue'))
Vue.component('sg-user', () => import('./components/core/user.vue'))
Vue.component('sg-user-current', () => import('./components/core/user-current.vue'))
Vue.component('sg-chart-pie', () => import('./components/core/chart-pie.vue'))
