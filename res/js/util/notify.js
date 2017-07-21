function createAlert (message, type) {
  const alert = document.createElement('div')
  alert.classList.add('alert')
  alert.classList.add('alert-page')
  alert.classList.add(`alert-${type}`)
  alert.innerHTML = message

  return alert
}

function createMessageFactory (type) {
  return function (message) {
    return new Promise((resolve) => {
      const alert = createAlert(message, type)

      alert.addEventListener('animationend', function remove () {
        alert.removeEventListener('animationend', remove, false)
        alert.remove()
        resolve()
      }, false)

      document.body.appendChild(alert)
      alert.classList.add('alert-auto')
    })
  }
}

const success = createMessageFactory('success')
const danger = createMessageFactory('danger')
const info = createMessageFactory('info')

export { success, danger, info }
