<template>
  <div class="poll-editor-simple form-modern">
    <ol class="poll-answers" v-if="answers.length > 0">
      <li v-for="(answer, index) in answers" :key="answer.rowIndex">
        <answer @remove="answers.splice(index, 1)">
          <simple-answer v-model="answer.value" />
        </answer>
      </li>
    </ol>
    <div class="poll-answers poll-answers-empty" v-else>
      <p>
        <em>Füge deiner Umfrage eine Antwort hinzu</em>
      </p>
    </div>
    <div class="btn-toolbar">
      <button type="button" class="btn btn-sm btn-primary" @click="addAnswer()">
        <i class="sg sg-add"></i>
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
    mixins: [AnswerEditorMixin],
    components: { Answer, SimpleAnswer },
    methods: {
      addAnswer () {
        this.newRow({
          title: ''
        })
      }
    }
  }
</script>
