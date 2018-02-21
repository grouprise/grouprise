<template>
  <poll-voter class="poll-simple" :poll="poll" :canVote="canVote" :isVoting="isVoting"
              @vote="startVote" ref="poll">
    <!-- custom poll header during vote -->
    <template slot="header" v-if="isVoting">
      <div class="poll-info">
        Du stimmst ab, indem du Antworten einzeln bewertest.
        <span class="content-nobreak"><i class="fa fa-thumbs-up"></i> für <em>Ja</em></span>,
        <span class="content-nobreak"><i class="fa fa-thumbs-down"></i> für <em>Nein</em></span>,
        <span class="content-nobreak"><i class="fa fa-circle"></i> für <em>Vielleicht</em></span>.
      </div>
    </template>

    <!-- custom poll footer during vote -->
    <div class="poll-actions" slot="footer" slot-scope="props" v-if="isVoting">
      <button type="button" class="btn btn-sm btn-primary"
              @click="submitVote(props.canSubmitVote)">
        Stimme abgeben
      </button>
    </div>

    <template v-if="poll">
      <div class="poll-answers">
        <poll-voter-answer :option="option"
                           v-show="showAllOptions || index < showThreshold"
                           v-for="(option, index) in rankedOptions" :key="option.id">
          <div slot="actions" v-if="!isVoting">
            <sg-chart-pie :data="optionRatings[option.id]" size="2.5rem" />
          </div>
          <div slot="actions" v-if="isVoting">
            <button type="button" class="btn btn-default poll-endorse-yes"
                    title="Vorschlag unterstützen"
                    :aria-pressed="endorsements[option.id] === true ? 'true' : 'false'"
                    @click="endorsements[option.id] = true">
              <i class="fa fa-thumbs-up"></i>
            </button>
            <button type="button" class="btn btn-default poll-btn poll-endorse-maybe"
                    title="Ist mir egal"
                    :aria-pressed="endorsements[option.id] === null ? 'true' : 'false'"
                    @click="endorsements[option.id] = null">
              <i class="fa fa-circle"></i>
            </button>
            <button type="button" class="btn btn-default poll-btn poll-endorse-no"
                    title="Vorschlag ablehnen"
                    :aria-pressed="endorsements[option.id] === false ? 'true' : 'false'"
                    @click="endorsements[option.id] = false">
              <i class="fa fa-thumbs-down"></i>
            </button>
          </div>
        </poll-voter-answer>

        <div class="btn-toolbar btn-toolbar-centered"
             v-if="!showAllOptions && rankedOptions.length > showThreshold"
             @click="showAllOptions = true">
          <button type="button" class="btn btn-sm btn-default">Restliche Optionen zeigen</button>
        </div>
      </div>
    </template>
  </poll-voter>
</template>

<script>
  import { find, values, sum } from 'lodash'

  import PollVoter from './poll-voter.vue'
  import PollVoterAnswer from './poll-voter-answer.vue'
  import { rankOptions } from './poll-helpers'

  export default {
    components: { PollVoter, PollVoterAnswer },
    props: {
      poll: Object,
      canVote: Boolean
    },
    data () {
      return {
        isVoting: false,
        showAllOptions: false,
        showThreshold: 5,
        endorsements: null
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