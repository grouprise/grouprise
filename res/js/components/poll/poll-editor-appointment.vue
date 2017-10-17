<template>
  <div class="poll-editor-appointment form-modern">
    <ol class="poll-answers" v-if="answers.length > 0">
      <li v-for="(answer, index) in answers" :key="answer.rowIndex">
        <answer @remove="removeRow(index)">
          <appointment-answer v-model="answer.value" />
        </answer>
      </li>
    </ol>
    <div class="poll-answers poll-answers-empty" v-else>
      <p>
        <em>Füge deiner Terminumfrage einen Termin hinzu</em>
      </p>
    </div>
    <div class="btn-toolbar">
      <button type="button" class="btn btn-sm btn-primary" @click="addAnswer()">
        <i class="sg sg-add"></i>
        Termin hinzufügen
      </button>
    </div>
  </div>
</template>

<script>
  import Answer from './poll-answer.vue'
  import AnswerEditorMixin from './answer-editor-mixin'
  import AppointmentAnswer from './poll-editor-appointment-answer.vue'

  function newDate (ref = null) {
    if (ref) {
      return new Date(ref.getTime())
    } else {
      const date = new Date()
      date.setHours(12)
      date.setMinutes(0)
      return date
    }
  }

  export default {
    components: { Answer, AppointmentAnswer },
    mixins: [AnswerEditorMixin],
    methods: {
      addAnswer () {
        const lastAnswer = this.answers[this.answers.length - 1]
        this.newRow({
          start: newDate(lastAnswer ? lastAnswer.value.start : null),
          duration: null
        })
      }
    }
  }
</script>
