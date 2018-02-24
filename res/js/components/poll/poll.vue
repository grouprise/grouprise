<template>
  <component :is="voter" :poll="poll" :canVote="canVote" />
</template>

<script>
  import { poll } from '../../adapters/api'
  import VoterCondorcet from './poll-voter-condorcet.vue'
  import VoterSimple from './poll-voter-simple.vue'

  export default {
    props: {
      pollId: Number,
      canVote: Boolean,
      type: String
    },
    data () {
      return {
        poll: null
      }
    },
    computed: {
      voter () {
        switch (this.type) {
          case 'simple': return VoterSimple
          case 'condorcet': return VoterCondorcet
        }
      }
    },
    provide () {
      return {
        controller: {
          refreshPoll: this.refreshPoll
        }
      }
    },
    methods: {
      async refreshPoll () {
        this.poll = null
        const _poll = await poll.get(this.pollId)
        this.poll = _poll
        return _poll
      }
    },
    async created () {
      this.refreshPoll()
    }
  }
</script>
