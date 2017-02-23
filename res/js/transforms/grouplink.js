import Vue from 'vue'
import randomId from 'random-id'
import { on, remove, addClass, matchesMedia } from 'luett'
import { group as api } from '../adapters/api'
import GroupPreview from '../content/components/group-preview.vue'

const cache = {}

export default (el, opts) => {
  const time = opts.conf.time || 250
  const { ref } = opts.conf
  let vue
  let container
  let action
  let isCreated = false
  const data = { show: false }

  const enterListener = on(el, 'mouseenter', matchesMedia.min.medium(show))
  const leaveListener = on(el, 'mouseleave', matchesMedia.min.medium(hide))

  function show() {
    clearTimeout(action)
    setTimeout(() => data.show = true, time)

    if(!isCreated) {
      createElement()
    }
  }

  function hide() {
    clearTimeout(action)
    setTimeout(() => data.show = false, time)
  }

  function get() {
    return cache[ref]
      ? Promise.resolve(cache[ref])
      : api.single(ref).then(group => {
        cache[ref] = group
        return group
      })
  }

  function createElement() {
    isCreated = true
    return get()
      .then(group => {
        data.group = group
        vue = new Vue({
          template: `<transition name='fade-down' appear>
                        <group-preview v-if='show' :group="group"></group-preview>
                     </transition>`,
          el: `#${container.id}`,
          data: data,
          components: { GroupPreview }
        })
      })
  }

  addClass(el, 'group-link')
  container = document.createElement('div')
  container.id = `group-link-${randomId(6)}`
  el.appendChild(container)

  return {
    remove() {
      enterListener.destroy()
      leaveListener.destroy()

      if (vue) {
        vue.$destroy()
      }

      if (container) {
        remove(container)
      }
    }
  }
}
