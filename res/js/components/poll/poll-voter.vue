<template>
  <div
    class="poll"
    :class="{ 'poll-voting': isVoting, 'poll-loading': !poll }"
  >
    <header class="poll-header">
      <i
        v-if="isVoting"
        class="poll-header-icon sg sg-poll-info"
      />
      <slot name="header">
        <div class="poll-info">
          <div>{{ headerText }}</div>
          <small
            v-if="lastVoted"
            class="content-mute"
          >
            Letztes Votum {{ lastVoted.from(new Date()) }}
          </small>
        </div>
        <div class="poll-header-actions">
          <div
            v-if="!poll"
            class="spinner"
          />
          <button
            v-if="poll && allowVote"
            type="button"
            class="btn btn-primary btn-sm"
            @click="notifyVote"
          >
            Jetzt abstimmen
          </button>
        </div>
      </slot>
    </header>
    <div
      v-if="poll"
      class="poll-body"
    >
      <slot />
    </div>
    <footer
      v-if="poll && allowVote"
      class="poll-footer"
    >
      <keep-alive>
        <sg-user-current
          v-model="user"
          :anonymous-edit="true"
          :anonymous-login="true"
          @edit="notifyVote"
        />
      </keep-alive>
      <slot
        name="footer"
        :canSubmitVote="user && user.name"
      />
    </footer>
  </div>
</template>

<script>
  import { get } from 'lodash'
  import moment from 'moment'
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
        user: null,
        hasGestaltVoted: false
      }
    },
    computed: {
      lastVoted () {
        return this.poll && this.poll.last_voted
          ? moment(this.poll.last_voted)
          : null
      },
      allowVote () {
        return this.canVote && !this.hasGestaltVoted
      },
      headerText () {
        const { poll, allowVote } = this
        const numVotes = poll ? poll.votes.length : null
        return poll === null
          ? 'Lade Abstimmungsdaten...'
          : numVotes === 0
            ? 'Bisher hat noch keine Person ihre Stimme abgegeben. Sei die erste!'
            : `Es ${numVotes === 1 ? 'hat' : 'haben'} bisher ${numVotes > 1 ? `${numVotes} Personen` : 'eine Person'} ihre Stimme abgegeben. ${allowVote ? 'Sei die nächste!' : 'Du hast bereits abgestimmt.'}`
      }
    },
    inject: ['controller'],
    watch: {
      user () {
        this.$emit('user', this.user)
      }
    },
    methods: {
      notifyVote () {
        if (!this.isVoting && this.allowVote) {
          this.$emit('vote')
        }
      },
      async vote (data) {
        const user = this.user
        return poll.vote(this.poll.id, {...data, gestalt: this.user})
          .then(
            () => {
              // if we have a non-anon user we set the hasVoted flag
              // anon-users may vote multiple times as multiple people might use the
              // same computer + browser session for it
              if (this.user.id !== null) {
                this.hasGestaltVoted = true
              }
              return this.controller.refreshPoll()
            },
            err => {
              const status = get(err, 'response.status', 500)
              if (status === 403) {
                danger(`Deine Stimme konnte nicht gezählt werden. Vielleicht hat schon jemand
                mit diesem Namen abgestimmt?`)
              } else {
                danger(`Ups... da ist was schief gelaufen. Du kannst es gerne noch einmal probieren
          oder es später noch einmal probieren.`)
              }
              throw err
            }
          )
          .then(() => success(`Deine Stimme wurde gezählt ${user.name}. Danke!`))
      },
      requestUserName () {
        danger('Bitte gib einen Namen ein oder melde dich an')
      }
    }
  }
</script>

