<template>
  <poll-voter
    ref="poll"
    class="poll-condorcet"
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
        Du stimmst ab, indem du die Antworten nach deiner Vorliebe sortierst. Verschiebe sie
        oder nutze die Pfeile rechts, um ihre Position zu verändern.
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
      <!-- simple poll answer list when not voting -->
      <div
        v-if="!isVoting"
        class="poll-answers"
      >
        <poll-voter-answer
          v-for="(option, index) in rankedOptions"
          v-show="!optionsShorted || index < showThreshold"
          :key="option.id"
          :option="option"
          :data-index="index + 1"
        />
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

      <!-- draggable poll answers during vote -->
      <draggable
        v-else
        v-model="rankedOptions"
        :options="{ animation: 150 }"
      >
        <transition-group
          class="poll-answers poll-answers-draggable"
          tag="div"
        >
          <poll-voter-answer
            v-for="(option, index) in rankedOptions"
            :key="option.id"
            :option="option"
            :data-index="index + 1"
          >
            <div slot="actions">
              <button
                type="button"
                class="btn btn-default btn-sm"
                :disabled="index === 0"
                title="Diese Option weiter nach oben sortieren"
                @click="_moveOption(option.id, -1)"
              >
                <i class="sg sg-order-up" />
              </button>
              <button
                type="button"
                class="btn btn-default btn-sm"
                :disabled="index + 1 === rankedOptions.length"
                title="Diese Option weiter nach unten sortieren"
                @click="_moveOption(option.id, +1)"
              >
                <i class="sg sg-order-down" />
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
    name: 'GrouprisePollCondorcetVoter',
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
