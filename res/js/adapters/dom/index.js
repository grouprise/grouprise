import { $ } from 'luett'

export function inputAdapter (el) {
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

export function selectAdapter (el) {
  return {
    emptyOption: '',
    get () {
      return {
        value: el.options[el.selectedIndex].value,
        name: el.options[el.selectedIndex].textContent
      }
    },
    set (valueObj, propagate = false) {
      const value = valueObj.value

      if (value && !$(`[value="${valueObj.value}"]`, el)) {
        const option = document.createElement('option')
        option.value = valueObj.value
        option.textContent = valueObj.name
        el.appendChild(option)
      }

      el.value = value === null ? this.emptyOption : value

      if (propagate) {
        el.dispatchEvent(new window.Event('change'))
      }
    }
  }
}

export function valueSubmissionAdapter (inputAdapter, submit) {
  const iface = {
    get: (...args) => inputAdapter.get(...args),
    set: (valueObj, ...args) => {
      const currentValue = iface.get().value
      inputAdapter.set(valueObj, ...args)
      if (currentValue !== valueObj.value) {
        if (!submit) {
          console.error('tried to auto-submit value but submit is missing')
        } else {
          submit.click()
        }
      }
    }
  }
  return iface
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
