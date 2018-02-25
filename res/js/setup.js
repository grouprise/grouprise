import 'object-assign-shim'
import 'matches-selector-polyfill/dist/matches-selector-polyfill'
import 'es6-promise/auto'
import 'modernizr'
import Vue from 'vue'

// third-party vue plugins / components
import draggable from 'vuedraggable'

// custom global vue components
import FilePicker from './components/core/file-picker.vue'
import ImagePicker from './components/image/image-picker.vue'
import Select from './components/core/select.vue'
import Avatar from './components/core/avatar.vue'
import DateTime from './components/time/datetime.vue'
import NumberSpinner from './components/core/number-spinner.vue'
import Switch from './components/core/switch.vue'
import Configurator from './components/core/configurator.vue'
import Input from './components/core/input.vue'
import User from './components/core/user.vue'
import UserCurrent from './components/core/user-current.vue'
import ChartPie from './components/core/chart-pie.vue'

// custom global vue filters
import { fallback, truncatewords } from './components/core/filters.js'

// vue setup
Vue.filter('default', fallback)
Vue.filter('truncatewords', truncatewords)
Vue.component('draggable', draggable)
Vue.component('sg-file-picker', FilePicker)
Vue.component('sg-image-picker', ImagePicker)
Vue.component('sg-input', Input)
Vue.component('sg-select', Select)
Vue.component('sg-avatar', Avatar)
Vue.component('sg-datetime', DateTime)
Vue.component('sg-number-spinner', NumberSpinner)
Vue.component('sg-switch', Switch)
Vue.component('sg-configurator', Configurator)
Vue.component('sg-user', User)
Vue.component('sg-user-current', UserCurrent)
Vue.component('sg-chart-pie', ChartPie)
