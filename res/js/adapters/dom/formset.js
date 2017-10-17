import { find, groupBy, partial as p } from 'lodash'
import { $, $$, attr } from 'luett'

const name = attr('name')
const prefixName = '__prefix__'
const prefixRegex = new RegExp(`^.+-${prefixName}-(.+)$`)
const rowRegex = /^.+-([0-9]+)-(.+)$/

const defineProperty = (obj, property, getter, setter = null) => {
  Object.defineProperty(obj, property, {
    get: getter,
    enumerable: true,
    ...(setter ? {
      set: setter,
      configurable: true
    } : {})
  })
}

const createElement = html => {
  const div = document.createElement('div')
  div.innerHTML = html
  return div
}

const resolveInputTypes = input => {
  const tag = input.tagName.toLowerCase()
  const inputType = tag === 'input' ? input.type : null
  return { tag, inputType }
}

const resolveRowData = name => {
  const prefixMatch = name.match(prefixRegex)
  const rowMatch = name.match(rowRegex)
  let propertyName, rowIndex

  if (prefixMatch) {
    propertyName = prefixMatch[1]
  } else if (rowMatch) {
    [, rowIndex, propertyName] = rowMatch
  }

  return { propertyName, rowIndex }
}

const setInputValue = (input, value) => {
  const { tag, inputType } = resolveInputTypes(input)

  if (tag === 'textarea') {
    input.textContent = value
  } else if (inputType === 'checkbox') {
    input.checked = Boolean(value)
  } else if (inputType === 'radio' && input.value === value) {
    // todo this is obviously broken because radio inputs should be handled as compound field
    input.checked = Boolean(value)
  } else {
    input.value = value
  }
}

const getInputValue = input => {
  const { tag, inputType } = resolveInputTypes(input)

  if (tag === 'textarea') {
    return input.textContent
  } else if (inputType === 'checkbox' || inputType === 'radio') {
    return input.checked
  } else {
    return input.value
  }
}

const findField = (fields, name) => {
  return find(fields, field => field.propertyName === name)
}

const withData = (fields, data, handler) => {
  let result = null
  data.forEach(fieldData => {
    const { name, value } = fieldData
    const field = findField(fields, name)
    if (!field) {
      throw Error(`unknown data field '${name}'`)
    }
    result = handler(field, name, value)
  })
  return result
}

const createRow = (fields, data, index) => {
  const div = document.createElement('div')
  withData(fields, data, (field, name, value) => {
    div.appendChild(field.create(value, index))
  })
  return div
}

const setData = (fields, data) => {
  withData(fields, data, (field, name, value) => {
    field.value = value
  })
}

const deleteRow = (fields, shouldDelete = true) => {
  withData(fields, [{ name: 'DELETE' }], field => {
    field.value = shouldDelete
  })
}

const isRowDeleted = fields => {
  return withData(fields, [{ name: 'DELETE' }], field => field.value)
}

const resolveFormFields = form => {
  form = typeof form === 'string'
    ? createElement(form)
    : form.tagName === 'SCRIPT'
    ? createElement(form.innerHTML)
    : form
  return $$('input, select, textarea', form)
    .map(input => {
      const { tag, inputType } = resolveInputTypes(input)
      const required = input.required
      const disabled = input.disabled
      const maxLength = input.maxlength
      const id = input.id || ''
      const name = input.name || ''
      const value = input.value
      const { propertyName, rowIndex } = resolveRowData(name)
      const create = (value, index) => {
        const node = input.cloneNode(false)
        setInputValue(node, value)
        node.id = id.replace(prefixName, index)
        node.name = name.replace(prefixName, index)
        return node
      }
      const result = {
        tag,
        inputType,
        required,
        disabled,
        maxLength,
        id,
        name,
        propertyName,
        rowIndex,
        value,
        create
      }
      defineProperty(result, 'value', p(getInputValue, input), p(setInputValue, input))
      return result
    })
    .filter(field => field)
}

const createRowAdapter = (fields, index) => {
  const iface = {
    fields,
    index,
    field: name => findField(fields, name),
    setData: data => {
      setData(fields, data)
      return iface
    }
  }
  defineProperty(iface, 'delete', p(isRowDeleted, fields), p(deleteRow, fields))
  return iface
}

const resolveRows = form => {
  const rows = groupBy(resolveFormFields(form), input => input.rowIndex)
  return Object.keys(rows)
    .map(name => {
      if (name === 'undefined') return
      const fields = rows[name]
      return createRowAdapter(fields, parseInt(name))
    })
    .filter(group => group)
}

const resolveData = (defaults, data) => {
  return defaults.filter(defaultData => {
    for (const fieldData of data) {
      if (defaultData.name === fieldData.name) {
        return false
      }
    }
    return true
  }).concat(data)
}

export default (formsetEl, options = { name: 'form' }) => {
  const iface = {}
  const exampleForm = $('[data-formset-example]', formsetEl)
  const totalForms = name.$(`${options.name}-TOTAL_FORMS`)
  const initialForms = name.$(`${options.name}-INITIAL_FORMS`)
  const minNumForms = name.$(`${options.name}-MIN_NUM_FORMS`)
  const maxNumForms = name.$(`${options.name}-MAX_NUM_FORMS`)

  const createIndex = () => {
    return Math.max(...rows.map(row => row.index)) + 1
  }

  const createTemplateRow = form => {
    const fields = resolveFormFields(form)
    const templateIface = {
      fields,
      createRow: (data, index = null) => {
        if (templateIface.totalForms >= maxNumForms) {
          throw new Error('cannot add row. maximum number reached')
        }
        index = index || createIndex()
        totalForms.value = iface.totalForms + 1
        const rowEl = createRow(fields, resolveData(iface.rowDefaults, data), index)
        const row = createRowAdapter(resolveFormFields(rowEl), index)
        rows.push(row)
        formsetEl.appendChild(rowEl)
        return templateIface
      }
    }
    return templateIface
  }

  const rows = resolveRows(formsetEl)
  const templateRow = createTemplateRow(exampleForm)

  defineProperty(iface, 'totalForms', () => parseInt(totalForms.value))
  defineProperty(iface, 'initialForms', () => parseInt(initialForms.value))
  defineProperty(iface, 'minNumForms', () => parseInt(minNumForms.value))
  defineProperty(iface, 'maxNumForms', () => parseInt(maxNumForms.value))
  defineProperty(iface, 'templateRow', () => templateRow)
  defineProperty(iface, 'rows', () => rows)
  defineProperty(iface, 'dataArrayFromObject', () => data => {
    return Object.keys(data).map(name => ({ name, value: data[name] }))
  })
  defineProperty(iface, 'findRow', () => index => find(rows, row => row.index === index))
  iface.rowDefaults = [
    { name: 'DELETE', value: false }
  ]

  return iface
}
