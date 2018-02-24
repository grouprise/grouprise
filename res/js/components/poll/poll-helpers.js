import { flow, sortBy, map, indexOf } from 'lodash'
import { createInitials } from '../../util/strings'

export function rankedIndexOf (collection, value) {
  const index = indexOf(collection, value)
  return 1 + (index === -1 ? collection.length : index)
}

export function createAnonUserStub (name) {
  return {
    id: null,
    name,
    initials: createInitials(name),
    about: null,
    avatar: null,
    avatar_color: null
  }
}

export function rankOptions ({options, ranking, winner, votes}, validOptionVote) {
  return flow([
    options => sortBy(options, [option => rankedIndexOf(ranking, option.id)]),
    options => map(options, option => {
      return {
        ...option,
        isWinner: option.id === winner,
        voters: votes
          .filter(vote => validOptionVote({vote, option}))
          .map(vote => vote.voter)
          .map(voter => typeof voter !== 'string' ? voter : createAnonUserStub(voter))
      }
    })
  ])(options)
}

export const pollVoterMixin = {
  props: {
    poll: Object,
    canVote: Boolean
  },
  data () {
    return {
      isVoting: false,
      showAllOptions: false,
      showThreshold: 5
    }
  },
  computed: {
    optionsShorted () {
      return !this.isVoting &&
        !this.showAllOptions &&
        this.rankedOptions.length > this.showThreshold
    }
  }
}
