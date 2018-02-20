<template>
  <div class="poll" :class="{ 'poll-voting': isVoting, 'poll-loading': !poll }">
    <header class="poll-header">
      <i class="poll-header-icon fa fa-lightbulb-o" v-if="isVoting"></i>
      <slot name="header">
        <div class="poll-info">
          {{ headerText }}
        </div>
        <div class="poll-header-actions">
          <div class="spinner" v-if="!poll"></div>
          <button type="button" class="btn btn-primary btn-sm" @click="$emit('vote')"
                  v-if="poll && canVote">
            Jetzt abstimmen
          </button>
        </div>
      </slot>
    </header>
    <div class="poll-body" v-if="poll">
      <slot />
    </div>
    <footer class="poll-footer" v-if="poll && canVote">
      <keep-alive>
        <sg-user-current :anonymousEdit="true" :anonymousLogin="true" v-model="user"
                         @edit="$emit('vote')" />
      </keep-alive>
      <slot name="footer" :canSubmitVote="user && user.name" />
    </footer>
  </div>
</template>

<script>
  import { poll } from '../../adapters/api'
  import { danger, success } from '../../util/notify'

  export default {
    props: {
      poll: Object,
      canVote: Boolean,
      isVoting: Boolean
    },
    data () {
      return {
        user: null
      }
    },
    computed: {
      headerText () {
        const { poll, canVote } = this
        const numVotes = poll ? poll.votes.length : null
        return poll === null
          ? 'Lade Abstimmungsdaten...'
          : numVotes === 0
            ? 'Bisher hat noch keine Person ihre Stimme abgegeben. Sei die erste!'
            : `Es haben bisher ${numVotes > 1 ? `${numVotes} Personen` : 'eine Person'} ihre Stimme abgegeben. ${canVote ? 'Sei die nächste!' : 'Du hast bereits abgestimmt.'}`
      }
    },
    inject: ['controller'],
    methods: {
      async vote (data) {
        const user = this.user
        return poll.vote(this.poll.id, {...data, gestalt: this.user})
          .then(() => {
            this.username = null
            return this.controller.refreshPoll()
          })
          .then(() => success(`Deine Stimme wurde gezählt ${user.name}. Danke!`))
      },
      requestUserName () {
        danger('Bitte gib einen Namen ein oder melde dich an')
      }
    },
    watch: {
      user () {
        this.$emit('user', this.user)
      }
    }
  }
</script>

