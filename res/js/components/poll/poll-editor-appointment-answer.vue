<template>
  <!-- eslint-disable vue/no-mutating-props -->
  <!-- TODO: fix prop mutation */ -->

  <div class="datetime-row">
    <sg-datetime
      v-model="answer.start"
      :enable-time="true"
      :show-labels="true"
      date-label="Datum"
      time-label="Uhrzeit"
      :time-default="[12,0,0]"
    />
    <div class="datetime-duration">
      <button
        v-if="answer.duration === null"
        type="button"
        class="btn btn-default btn-sm"
        @click="toggleDuration()"
      >
        Dauer angeben
      </button>
      <sg-number-spinner
        v-else
        v-model="answer.duration"
        :step="1"
        :min="1"
        :label="durationLabel"
      />
    </div>
  </div>
</template>

<script>
  /* eslint-disable vue/no-mutating-props */
  /* TODO: fix prop mutation */

  export default {
    name: 'GroupriseAppointmentPollEditorAnswer',
    model: {
      prop: 'answer'
    },
    props: {
      answer: Object
    },
    computed: {
      durationLabel () {
        return this.answer.duration === 1 ? 'Stunde' : 'Stunden'
      }
    },
    methods: {
      toggleDuration () {
        if (this.answer.duration !== null) {
          this.answer.duration = null
        } else {
          this.answer.duration = 1
        }
      }
    }
  }
</script>
