import Snake from './transforms/snake'

Snake(document.querySelector('.snake'), {
  onFinish: () => { window.location.reload(true) }
})
