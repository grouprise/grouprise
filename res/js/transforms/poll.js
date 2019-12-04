import Vue from 'vue'
import PollVoter from '../components/poll/poll.vue'
import { createContainerAdapter } from '../util/dom'

export default (el, opts) => {
  const containerAdapter = createContainerAdapter(el)
  const state = {
    canVote: opts.conf.canVote === 'true',
    pollId: parseInt(opts.conf.id),
    type: opts.conf.type
  }

  const vue = new Vue({
    el: `#${containerAdapter.container.id}`,
    data: state,
    created () {
      containerAdapter.replacedEl.hide()
    },
    render (h) {
      return h(PollVoter, {
        props: {
          canVote: this.canVote,
          pollId: this.pollId,
          type: this.type
        }
      })
    }
  })

  return {
    remove () {
      vue.$destroy()
      containerAdapter.replacedEl.show()
      containerAdapter.destroy()
    }
  }
}
