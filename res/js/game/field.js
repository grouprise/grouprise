import { values } from './util'
import comparison from './comparison'

function random (min, max) {
  return Math.floor(Math.random() * (max - min)) + min
}

function Field (size, initial = 0) {
  const field = []
  const iface = {}

  for (let i = 0; i < size; i++) {
    field[i] = values(initial, size)
  }

  function get (pos) {
    return field[pos[0]][pos[1]]
  }

  function set (pos, val) {
    field[pos[0]][pos[1]] = val
    return iface
  }

  function replace (list, val) {
    const current = getFilled(val, comparison.equality)
    current.forEach((tile) => { set(tile.pos, initial) })
    list.forEach((pos) => { set(pos, val) })
    return iface
  }

  function neighbor (pos, direction) {
    switch (direction) {
      case 'left':
        return pos[0] === 0
          ? [size - 1, pos[1]] : [pos[0] - 1, pos[1]]
      case 'right':
        return pos[0] === size - 1
          ? [0, pos[1]] : [pos[0] + 1, pos[1]]
      case 'up':
        return pos[1] === 0
          ? [pos[0], size - 1] : [pos[0], pos[1] - 1]
      case 'down':
        return pos[1] === size - 1
          ? [pos[0], 0] : [pos[0], pos[1] + 1]
    }
  }

  function getFilled (value = initial, cmp = comparison.inequality) {
    const result = []

    for (let i = 0; i < size; i++) {
      for (let j = 0; j < size; j++) {
        if (cmp(field[i][j], value)) {
          result.push({
            pos: [i, j],
            val: field[i][j]
          })
        }
      }
    }

    return result
  }

  function empty () {
    while (true) {
      const randomPosition = [random(0, size - 1), random(0, size - 1)]

      if (get(randomPosition) === initial) {
        return randomPosition
      }
    }
  }

  Object.defineProperty(iface, 'size', { value: size, writable: false })
  Object.assign(iface, { get, set, replace, getFilled, neighbor, empty })
  return iface
}

export default Field
