<template>
  <div class="poll-editor">
    <tabs :storage="pollTypeStorage">
      <tab id="simple" name="Einfache Umfrage" v-if="!pollTypeStatic || pollType === 'simple'">
        <simple-editor v-model="answers" v-if="pollType === 'simple'" />
      </tab>
      <tab id="event" name="Terminumfrage" v-if="!pollTypeStatic || pollType === 'event'">
        <appointment-editor v-model="answers" v-if="pollType === 'event'" />
      </tab>
    </tabs>
  </div>
</template>

<script>
  import { Tabs, Tab } from 'vue-tabs-component'
  import AppointmentEditor from './poll-editor-appointment.vue'
  import SimpleEditor from './poll-editor-simple.vue'

  export default {
    components: {
      Tabs,
      Tab,
      AppointmentEditor,
      SimpleEditor
    },
    props: {
      answers: Array,
      pollType: String,
      pollTypeStatic: Boolean
    },
    data () {
      return {
        pollTypeStorage: () => ({
          get: () => `#${this.pollType}`,
          set: value => {
            const id = value.substr(1)
            if (id !== this.pollType) {
              this.$emit('switchPollType', id)
              return false
            } else {
              return true
            }
          }
        })
      }
    }
  }
</script>
