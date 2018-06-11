<template>
  <poll-voter class="poll-condorcet" :poll="poll" :canVote="canVote" :isVoting="isVoting"
              @vote="startVote" ref="poll">
    <!-- custom poll header during vote -->
    <template slot="header" v-if="isVoting">
      <div class="poll-info">
        Du stimmst ab, indem du die Antworten nach deiner Vorliebe sortierst. Verschiebe sie
        oder nutze die Pfeile rechts, um ihre Position zu verändern.
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
      <!-- simple poll answer list when not voting -->
      <div class="poll-answers"  v-if="!isVoting">
        <poll-voter-answer :option="option" :data-index="index + 1"
                           v-show="!optionsShorted || index < showThreshold"
                           v-for="(option, index) in rankedOptions" :key="option.id" />
        <div class="btn-toolbar btn-toolbar-centered" v-if="optionsShorted" @click="showAllOptions = true">
          <button type="button" class="btn btn-sm btn-default">Restliche Optionen zeigen</button>
        </div>
      </div>

      <!-- draggable poll answers during vote -->
      <draggable v-model="rankedOptions" :options="{ animation: 150 }" v-else>
        <transition-group class="poll-answers poll-answers-draggable" tag="div">
          <poll-voter-answer :option="option" :data-index="index + 1"
                             v-for="(option, index) in rankedOptions" :key="option.id">
            <div slot="actions">
              <button type="button" class="btn btn-default btn-sm" :disabled="index === 0"
                      title="Diese Option weiter nach oben sortieren"
                      @click="_moveOption(option.id, -1)">
                <i class="sg sg-order-up"></i>
              </button>
              <button type="button" class="btn btn-default btn-sm" :disabled="index + 1 === rankedOptions.length"
                      title="Diese Option weiter nach unten sortieren"
                      @click="_moveOption(option.id, +1)">
                <i class="sg sg-order-down"></i>
              </button>
            </div>
          </poll-voter-answer>
        </transition-group>
      </draggable>
    </template>
  </poll-voter>
</template>

<script>
  import move from 'lodash-move'

  import PollVoter from './poll-voter.vue'
  import PollVoterAnswer from './poll-voter-answer.vue'
  import { rankedIndexOf, rankOptions, pollVoterMixin } from './poll-helpers'

  export default {
    components: { PollVoter, PollVoterAnswer },
    mixins: [pollVoterMixin],
    data () {
      return {
        voteOrder: null
      }
    },
    computed: {
      rankedOptions: {
        get () {
          const { options, options_winner: winner, options_ranking: ranking, votes } = this.poll
          return rankOptions(
            { options, winner, ranking: this.voteOrder || ranking, votes },
            ({vote, option}) => rankedIndexOf(vote.ranking, option.id) === 1
          )
        },
        set (rankedOptions) {
          this.voteOrder = rankedOptions.map(option => option.id)
        }
      }
    },
    methods: {
      _moveOption (id, direction) {
        const currentIndex = this.voteOrder.indexOf(id)
        const newIndex = currentIndex + direction
        this.voteOrder = move(this.voteOrder, currentIndex, newIndex)
      },
      startVote () {
        this.isVoting = true
        this.voteOrder = this.rankedOptions.map(option => option.id)
      },
      async submitVote (canSubmitVote) {
        if (!canSubmitVote) {
          return this.$refs.poll.requestUserName()
        }

        const voteOrder = this.voteOrder
        this.voteOrder = null
        this.isVoting = false
        await this.$refs.poll.vote({
          ranking: voteOrder
        }).then(null, () => {
          this.voteOrder = voteOrder
          this.isVoting = true
        })
      }
    }
  }
</script>
