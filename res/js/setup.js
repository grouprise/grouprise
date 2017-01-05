import { $ } from 'luett'

// load config
window.app = {
  conf: JSON.parse($('#app-configuration').textContent)
}
