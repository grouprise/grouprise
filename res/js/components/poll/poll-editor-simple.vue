<template>
  <div class="poll-editor-simple form-modern">
    <ol
      v-if="answers.length > 0"
      class="poll-answers"
    >
      <li
        v-for="(answer, index) in answers"
        :key="answer.rowIndex"
      >
        <answer @remove="answers.splice(index, 1)">
          <simple-answer v-model="answer.value" />
        </answer>
      </li>
    </ol>
    <div
      v-else
      class="poll-answers poll-answers-empty"
    >
      <p>
        <em>Füge deiner Umfrage eine Antwort hinzu</em>
      </p>
    </div>
    <div class="btn-toolbar">
      <button
        type="button"
        class="btn btn-sm btn-primary"
        @click="addAnswer()"
      >
        <i class="sg sg-add" />
        Antwortmöglichkeit hinzufügen
      </button>
    </div>
  </div>
</template>

<script>
  import Answer from './poll-answer.vue'
  import AnswerEditorMixin from './answer-editor-mixin'
  import SimpleAnswer from './poll-editor-simple-answer.vue'

  export default {
    name: 'GroupriseSimplePollEditor',
    components: { Answer, SimpleAnswer },
    mixins: [AnswerEditorMixin],
    methods: {
      addAnswer () {
        this.newRow({
          title: ''
        })
      }
    }
  }
</script>
