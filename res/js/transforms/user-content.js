import emojiRegex from 'emoji-regex'

const filters = [
  function emoji (content) {
    return content.replace(emojiRegex(), "<span class='emoji' data-emoji='$&'></span>")
  }
]

export default (el, opts) => {
  const originalContent = el.innerHTML
  el.innerHTML = filters.reduce((content, filter) => filter(content, opts), originalContent)

  return {
    remove () { el.innerHTML = originalContent }
  }
}
