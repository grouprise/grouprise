export function createInitials (name, _default = '?') {
  if (!name) return _default
  return name
    .split(' ')
    .map(x => x.substr(0, 1).toUpperCase())
    .join('')
    .substr(0, 4)
}
