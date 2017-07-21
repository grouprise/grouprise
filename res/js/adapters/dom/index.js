import { $ } from 'luett'

function inputAdapter (el) {
  return {
    get () {
      return {
        value: el.value,
        name: null
      }
    },
    set (valueObj, propagate = false) {
      el.value = valueObj.value

      if (propagate) {
        el.dispatchEvent(new window.Event('change'))
      }
    }
  }
}

function selectAdapter (el) {
  return {
    get () {
      return {
        value: el.options[el.selectedIndex].value,
        name: el.options[el.selectedIndex].textContent
      }
    },
    set (valueObj, propagate = false) {
      if (!$(`[value="${valueObj.value}"]`, el)) {
        const option = document.createElement('option')
        option.value = valueObj.value
        option.textContent = valueObj.name
        el.appendChild(option)
      }

      el.value = valueObj.value

      if (propagate) {
        el.dispatchEvent(new window.Event('change'))
      }
    }
  }
}

export default el => {
  const tagName = (el.tagName || el).toLowerCase()

  switch (tagName) {
    case 'select':
      return selectAdapter(el)
    case 'input':
      return inputAdapter(el)
  }
}
