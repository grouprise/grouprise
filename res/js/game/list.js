import comparison from './comparison'

function List (length = 1) {
  const list = []
  const iface = {}

  let maxLength = length

  function drop () {
    list.shift()
    return iface
  }

  function has (val, cmp = comparison.equality) {
    for (let i = 0, length = list.length; i < length; i++) {
      if (cmp(list[i], val)) {
        return true
      }
    }

    return false
  }

  function append (item) {
    while (list.length === maxLength) {
      list.shift()
    }

    list.push(item)
    return iface
  }

  function increment () {
    maxLength++
    return iface
  }

  function decrement () {
    maxLength--
    return iface
  }

  Object.defineProperty(iface, 'values', {
    get: () => list.slice()
  })

  Object.assign(iface, { drop, append, has, increment, decrement })
  return iface
}

export default List
