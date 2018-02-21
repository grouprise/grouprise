<template>
  <div>
    <div style="margin: 2rem 0 -1rem 0" v-if="this.voteType.getType() !== 'hidden'">
      <div class="row">
        <div class="col-md-6" v-for="choice in voteTypes">
          <div class="form-group">
            <div class="btn btn-default"
                 :aria-pressed="myVoteType === choice.value ? 'true' : 'false'"
                 @click="myVoteType = choice.value">
              <poll-vote-type :choice="choice" />
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="poll poll-editor">
      <tabs :storage="pollTypeStorage">
        <tab id="simple" name="Einfache Umfrage" v-if="!pollType.isStatic || myPollType === 'simple'">
          <simple-editor v-model="answers" v-if="myPollType === 'simple'" />
        </tab>
        <tab id="event" name="Terminumfrage" v-if="!pollType.isStatic || myPollType === 'event'">
          <appointment-editor v-model="answers" v-if="myPollType === 'event'" />
        </tab>
      </tabs>
    </div>
  </div>
</template>

<script>
  import { Tabs, Tab } from 'vue-tabs-component'
  import AppointmentEditor from './poll-editor-appointment.vue'
  import SimpleEditor from './poll-editor-simple.vue'
  import PollVoteType from './poll-votetype.vue'

  export default {
    components: {
      Tabs,
      Tab,
      AppointmentEditor,
      SimpleEditor,
      PollVoteType
    },
    props: {
      answers: Array,
      pollType: Object,
      voteType: Object
    },
    data () {
      return {
        myVoteType: this.voteType.get().value,
        myPollType: this.pollType.get().value,
        pollTypeStorage: () => ({
          get: () => `#${this.myPollType}`,
          set: value => {
            const id = value.substr(1)
            if (id !== this.myPollType) {
              if (!this.pollType.isStatic) {
                this.pollType.set({ value: id })
              }

              return false
            } else {
              return true
            }
          }
        }),
        voteTypes: [
          {
            value: 'simple',
            name: 'Meiste Stimmen',
            icon: 'fa-thumbs-up',
            description: `Es wird mit Ja, Nein und Vielleicht abgestimmt. Der Vorschlag mit
            den meisten Ja-Stimmen gewinnt.`
          },
          {
            value: 'condorcet',
            name: 'Konsens (Condorcet)',
            icon: 'fa-commenting-o',
            description: `Antworten werden nach Vorliebe geordnet. Vorschläge mit dem größten
          Konsens gewinnen.`
          }
        ]
      }
    },
    watch: {
      myVoteType () {
        this.voteType.set({ value: this.myVoteType })
      }
    }
  }
</script>
