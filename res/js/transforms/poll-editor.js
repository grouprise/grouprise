import closest from 'closest'
import { $, on } from 'luett'
import Vue from 'vue'
import PollEditor from '../components/poll/poll-editor.vue'
import createAnswerTransformer from '../components/poll/answer-transformer'
import createDomAdapter, { valueSubmissionAdapter } from '../adapters/dom'
import createFormsetAdapter from '../adapters/dom/formset'
import { createDisplayControl, createContainerAdapter } from '../util/dom'

function createPollTypeAdapter (el) {
  const pollTypeEl = $('[data-poll-type]', el)
  const pollTypeSwitchEl = $('[data-poll-type-switch]', el)
  const pollType = valueSubmissionAdapter(createDomAdapter(pollTypeEl), pollTypeSwitchEl)
  return {
    isStatic: pollTypeEl.type === 'hidden',
    ...pollType
  }
}

export default el => {
  const formEl = closest(el, 'form')
  const pollTypeAdapter = createPollTypeAdapter(formEl)
  const containerAdapter = createContainerAdapter(el)
  const pollSettings = createDisplayControl($('[data-poll-settings]', formEl))
  const formsetAdapter = createFormsetAdapter(el, { name: 'form' })
  const answers = createAnswerTransformer(pollTypeAdapter, formsetAdapter)
  const state = {
    answers: answers.get()
  }

  const vue = new Vue({
    el: `#${containerAdapter.container.id}`,
    data: state,
    render (h) {
      return h(PollEditor, {
        props: {
          pollType: pollTypeAdapter.get().value,
          pollTypeStatic: pollTypeAdapter.isStatic,
          answers: this.answers
        },
        on: {
          switchPollType (id) {
            if (!pollTypeAdapter.isStatic) {
              pollTypeAdapter.set({ value: id })
            }
          }
        }
      })
    },
    created () {
      pollSettings.hide()
      containerAdapter.replacedEl.hide()
    }
  })

  const submitListener = on(formEl, 'submit', () => {
    answers.set(state.answers)
  })

  return {
    remove () {
      vue.$destroy()
      pollSettings.show()
      containerAdapter.replacedEl.show()
      containerAdapter.destroy()
      submitListener.destroy()
    }
  }
}
