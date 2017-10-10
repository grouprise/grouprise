export const fallback = (value, fallback) => {
  return !value ? fallback : value
}

export const truncatewords = (value, maxNumberOfWords) => {
  const parts = fallback(value, '').split(' ')
  return parts.length > maxNumberOfWords
    ? parts.slice(0, maxNumberOfWords).join(' ') + '...'
    : value
}
