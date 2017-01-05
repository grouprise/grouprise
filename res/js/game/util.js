function has (obj, key) {
  return Object.prototype.hasOwnProperty.call(obj, key)
}

function values (value, times) {
  const result = []

  for (let i = 0; i < times; i++) {
    result.push(value)
  }

  return result
}

export { values, has }
