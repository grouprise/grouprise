<template>
  <!-- eslint-disable vue/no-mutating-props -->
  <!-- TODO: fix prop mutation */ -->

  <div>
    <div
      v-if="voteType.getType() !== 'hidden'"
      style="margin: 2rem 0 -1rem 0"
    >
      <label
        id="vote-type-label"
        class="control-label"
      >
        Wie wird abgestimmt?
      </label>
      <div class="row">
        <div
          v-for="choice in voteTypes"
          :key="choice.value"
          class="col-md-6"
        >
          <div
            class="form-group"
            aria-labelledby="vote-type-label"
          >
            <div
              class="btn btn-plane"
              :aria-pressed="myVoteType === choice.value ? 'true' : 'false'"
              @click="myVoteType = choice.value"
            >
              <poll-vote-type :choice="choice" />
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="poll poll-editor">
      <tabs :storage="pollTypeStorage">
        <tab
          v-if="!pollType.isStatic || myPollType === 'simple'"
          id="simple"
          name="Einfache Umfrage"
        >
          <simple-editor
            v-if="myPollType === 'simple'"
            v-model="answers"
          />
        </tab>
        <tab
          v-if="!pollType.isStatic || myPollType === 'event'"
          id="event"
          name="Terminumfrage"
        >
          <appointment-editor
            v-if="myPollType === 'event'"
            v-model="answers"
          />
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
    name: 'GrouprisePollEditor',
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
            icon: 'poll-votetype-simple',
            description: `Es wird mit Ja, Nein und Vielleicht abgestimmt. Der Vorschlag mit
              den meisten Ja-Stimmen gewinnt. Super für Termine und klare Entscheidungen.`
          },
          {
            value: 'condorcet',
            name: 'Größte Gemeinsamkeit (Condorcet)',
            icon: 'poll-votetype-condorcet',
            description: `Antworten werden nach Vorliebe geordnet. Vorschläge mit dem größten
              Konsens gewinnen. Gut für Richtungsentscheidungen und Stimmungsbilder.`
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
