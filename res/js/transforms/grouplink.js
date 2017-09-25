import { on, remove, /* toggleClass, */ matchesMedia } from 'luett'
// import Popper from 'popper.js'
import randomId from 'random-id'
import Vue from 'vue'
import { group as api } from '../adapters/api'
import GroupPreview from '../components/content/group-preview.vue'

const cache = {}

function get (ref) {
  return cache[ref]
    ? Promise.resolve(cache[ref])
    : api.single(ref).then(group => {
      cache[ref] = group
      return group
    })
}

function createContainer () {
  const container = document.createElement('div')
  const preview = document.createElement('div')
  container.id = `group-link-${randomId(6)}`
  container.className = 'group-link'
  container.appendChild(preview)
  document.body.appendChild(container)
  return container
}

export default async (el, opts) => {
  function toggle (force) {
    clearTimeout(toggle.action)
    setTimeout(() => { data.visible = force }, time)
  }

  const time = opts.conf.time || 250
  const { ref } = opts.conf
  const group = await get(ref)
  const data = { group, visible: false }
  const container = createContainer()
  const vue = new Vue({
    el: container.firstChild,
    data: data,
    render (h) {
      return h(GroupPreview, {
        props: {
          group: this.group,
          visible: this.visible
        }
      })
    }
  })
  /*
  const popper = new Popper(el, container, {
    placement: 'bottom-start'
  })
  */
  const enterListener = on(el, 'mouseenter', matchesMedia.min.medium(() => { toggle(true) }))
  const leaveListener = on(el, 'mouseleave', matchesMedia.min.medium(() => { toggle(false) }))

  return {
    remove () {
      enterListener.destroy()
      leaveListener.destroy()
      vue.$destroy()
      remove(container)
    }
  }
}
