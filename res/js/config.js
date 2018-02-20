import { $ } from 'luett'

// app configuration
window.app = {
  conf: JSON.parse($('#app-configuration').textContent)
}
