<template>
  <component
    :is="voter"
    :poll="poll"
    :can-vote="canVote"
  />
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
        return null
      }
    },
    provide () {
      return {
        controller: {
          refreshPoll: this.refreshPoll
        }
      }
    },
    async created () {
      this.refreshPoll()
    },
    methods: {
      async refreshPoll () {
        this.poll = null
        const _poll = await poll.get(this.pollId)
        this.poll = _poll
        return _poll
      }
    }
  }
</script>
