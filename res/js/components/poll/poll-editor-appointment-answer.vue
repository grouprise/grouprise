<template>
  <div class="datetime-row">
    <sg-datetime v-model="answer.start" :enableTime="true" :showLabels="true"
                 dateLabel="Datum" timeLabel="Uhrzeit" :timeDefault="[12,0,0]"></sg-datetime>
    <div class="datetime-duration">
      <button type="button" class="btn btn-default btn-sm" @click="toggleDuration()" v-if="answer.duration === null">
        Dauer angeben
      </button>
      <sg-number-spinner v-model="answer.duration" :step="1" :min="1" :label="durationLabel" v-else></sg-number-spinner>
    </div>
  </div>
</template>

<script>
  export default {
    model: {
      prop: 'answer'
    },
    props: {
      answer: Object
    },
    methods: {
      toggleDuration () {
        if (this.answer.duration !== null) {
          this.answer.duration = null
        } else {
          this.answer.duration = 1
        }
      }
    },
    computed: {
      durationLabel () {
        return this.answer.duration === 1 ? 'Stunde' : 'Stunden'
      }
    }
  }
</script>
