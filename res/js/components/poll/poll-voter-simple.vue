<template>
  <poll-voter
    ref="poll"
    class="poll-simple"
    :poll="poll"
    :can-vote="canVote"
    :is-voting="isVoting"
    @vote="startVote"
  >
    <!-- custom poll header during vote -->
    <template
      v-if="isVoting"
      slot="header"
    >
      <div class="poll-info">
        Du stimmst ab, indem du Antworten einzeln bewertest.
        <span class="content-nobreak"><i :class="icons.yes" /> für <em>Ja</em></span>,
        <span class="content-nobreak"><i :class="icons.no" /> für <em>Nein</em></span>,
        <span class="content-nobreak"><i :class="icons.maybe" /> für <em>Vielleicht</em></span>.
      </div>
    </template>

    <!-- custom poll footer during vote -->
    <div
      v-if="isVoting"
      slot="footer"
      slot-scope="props"
      class="poll-actions"
    >
      <button
        type="button"
        class="btn btn-sm btn-primary"
        @click="submitVote(props.canSubmitVote)"
      >
        Stimme abgeben
      </button>
    </div>

    <template v-if="poll">
      <div class="poll-answers">
        <poll-voter-answer
          v-for="(option, index) in rankedOptions"
          v-show="!optionsShorted || index < showThreshold"
          :key="option.id"
          :option="option"
        >
          <div
            v-if="!isVoting"
            slot="actions"
          >
            <sg-chart-pie
              v-if="optionRatings[option.id]"
              :data="optionRatings[option.id]"
              size="2.5rem"
            />
          </div>
          <div
            v-if="isVoting"
            slot="actions"
          >
            <button
              type="button"
              class="btn btn-default poll-btn poll-endorse-yes"
              title="Vorschlag unterstützen"
              :aria-pressed="endorsements[option.id] === true ? 'true' : 'false'"
              @click="endorsements[option.id] = true"
            >
              <i :class="icons.yes" />
            </button>
            <button
              type="button"
              class="btn btn-default poll-btn poll-endorse-maybe"
              title="Ist mir egal"
              :aria-pressed="endorsements[option.id] === null ? 'true' : 'false'"
              @click="endorsements[option.id] = null"
            >
              <i :class="icons.maybe" />
            </button>
            <button
              type="button"
              class="btn btn-default poll-btn poll-endorse-no"
              title="Vorschlag ablehnen"
              :aria-pressed="endorsements[option.id] === false ? 'true' : 'false'"
              @click="endorsements[option.id] = false"
            >
              <i :class="icons.no" />
            </button>
          </div>
        </poll-voter-answer>

        <div
          v-if="optionsShorted"
          class="btn-toolbar btn-toolbar-centered"
          @click="showAllOptions = true"
        >
          <button
            type="button"
            class="btn btn-sm btn-default"
          >
            Restliche Optionen zeigen
          </button>
        </div>
      </div>
    </template>
  </poll-voter>
</template>

<script>
  import { find, values, sum } from 'lodash'

  import PollVoter from './poll-voter.vue'
  import PollVoterAnswer from './poll-voter-answer.vue'
  import { rankOptions, pollVoterMixin } from './poll-helpers'

  export default {
    name: 'GrouprisePollSimpleVoter',
    components: { PollVoter, PollVoterAnswer },
    mixins: [pollVoterMixin],
    data () {
      return {
        endorsements: null,
        icons: {
          yes: 'sg sg-poll-vote-yes',
          no: 'sg sg-poll-vote-no',
          maybe: 'sg sg-poll-vote-maybe'
        }
      }
    },
    computed: {
      rankedOptions () {
        const { options, options_winner: winner, options_ranking: ranking, votes } = this.poll
        return rankOptions(
          { options, winner, ranking, votes },
          ({vote, option}) => find(vote.endorsements, i => i.option === option.id).endorsement
        )
      },
      optionRatings () {
        return this.poll.options.reduce((result, option) => {
          const stats = this.poll.vote_counts.find(x => x.option === option.id)

          // return early if no one has answered the poll yet
          if (!stats) return result

          const total = sum(values(stats.counts))
          const r = (count, type, title) => ({
            percentage: count / total * 100,
            classes: `chart-color-${type}`,
            title: `${count} / ${total} ${title}`
          })
          result[option.id] = [
            r(stats.counts.yes, 'success', 'Ja-Stimmen'),
            r(stats.counts.maybe, 'warning', 'Vielleicht-Stimmen'),
            r(stats.counts.no, 'danger', 'Nein-Stimmen')
          ]
          return result
        }, {})
      }
    },
    methods: {
      startVote () {
        this.isVoting = true
        this.endorsements = this.poll.options.reduce((result, option) => {
          result[option.id] = null
          return result
        }, {})
      },
      async submitVote (canSubmitVote) {
        if (!canSubmitVote) {
          return this.$refs.poll.requestUserName()
        }

        const endorsements = this.endorsements
        this.endorsements = null
        this.isVoting = false
        await this.$refs.poll.vote({
          endorsements: Object.keys(endorsements).map(id => ({
            option: id,
            endorsement: endorsements[id]
          }))
        }).then(null, () => {
          this.endorsements = endorsements
          this.isVoting = true
        })
      }
    }
  }
</script>
