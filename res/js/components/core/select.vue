<template>
  <div
    :id="componentId.wrapper"
    v-on-click-outside="dismissSelect"
    class="select"
    :class="selectClasses"
    @keydown.esc="closeFinder"
  >
    <div
      ref="current"
      class="select-current"
      tabindex="0"
      @click.prevent="toggleFinder()"
      @keydown="typeSelect"
    >
      <slot
        name="current-choice"
        :choice="currentChoice"
      >
        <component
          :is="renderer"
          v-if="currentChoice"
          :choice="currentChoice"
        />
      </slot>
      <slot name="no-result">
        <div
          v-if="!currentChoice"
          class="select-default"
        >
          {{ texts.noSelection }}
        </div>
      </slot>
      <div
        v-if="isDismissable"
        class="select-decorator select-dismiss"
        :style="decoratorStyle"
        @click.prevent.stop="dismissChoice"
      >
        <i>×</i>
      </div>
      <div
        v-else
        class="select-decorator select-caret"
        :style="decoratorStyle"
      >
        <i>▼</i>
      </div>
    </div>
    <transition :name="finderBelow ? 'fade-down' : 'fade-up'">
      <div
        v-show="showFinder"
        ref="finder"
        class="select-finder"
      >
        <div
          v-if="filter && choices.length > searchThreshold"
          class="select-search"
        >
          <label
            :for="componentId.search"
            class="sr-only"
          >{{ texts.searchLabel }}</label>
          <input
            :id="componentId.search"
            ref="search"
            v-model="currentSearch"
            type="search"
            class="select-search-input"
            :placeholder="texts.searchPlaceholder"
            @keydown.down.prevent="focusChoices"
            @keydown.enter.prevent="maybeSelect"
          >
          <span class="select-search-count">{{ availableChoices.length }}</span>
        </div>

        <ol
          v-if="availableChoices.length > 0"
          ref="choices"
          class="select-choices"
          @keydown.up.prevent="prevChoice"
          @keydown.down.prevent="nextChoice"
        >
          <li
            v-for="(choice, index) in availableChoices"
            :key="index"
            :data-value="choice.value"
            tabindex="0"
            @click="select(choice)"
            @keydown.enter="select(choice)"
          >
            <slot
              name="choice"
              :choice="choice"
              :index="index"
            >
              <component
                :is="renderer"
                :choice="choice"
                :index="index"
              />
            </slot>
          </li>
        </ol>
        <p
          v-else
          class="select-no-results"
        >
          {{ texts.noResult }}
        </p>
      </div>
    </transition>
  </div>
</template>

<script>
  import { mixin as onClickOutside } from 'vue-on-click-outside'
  import { includes, matches, find, findIndex, isFunction, isBoolean, throttle } from 'lodash'
  import randomId from 'random-id'

  const defaultFilter = (term, choice) => {
    return !term || (
      includes(choice.label.toLowerCase(), term) ||
      includes(choice.value.toLowerCase(), term) ||
      includes(choice.text.toLowerCase(), term)
    )
  }

  const typeFilter = (term, choice) => {
    return choice.label.toLowerCase().indexOf(term) === 0 || choice.text.toLowerCase().indexOf(term) === 0
  }

  export default {
    name: 'GroupriseSelect',
    mixins: [onClickOutside],
    props: {
      id: {
        type: String,
        default: () => randomId(20, 'a')
      },
      texts: {
        type: Object,
        default: () => ({
          searchPlaceholder: 'Suche nach Einträgen',
          searchLabel: 'Suche',
          noResult: 'Keine Ergebnisse gefunden 😔',
          noSelection: 'Keine Auswahl'
        })
      },
      renderer: Object,
      defaultValue: [String, Number],
      defaultChoice: Object,
      value: {
        type: [Number, String],
        default: null
      },
      choices: {
        type: Array,
        required: true
      },
      filter: {
        type: [Boolean, Function],
        default: () => defaultFilter
      },
      searchThreshold: {
        type: Number,
        default: 5
      }
    },
    data () {
      return {
        currentValue: null,
        showFinder: false,
        currentSearch: '',
        typedSearch: '',
        typedTimer: null,
        size: 0,
        finderSize: 0,
        resizeListener: null,
        scrollListener: null,
        finderBelow: true
      }
    },
    computed: {
      selectClasses () {
        return {
          'select-open': this.showFinder,
          'select-bottom': this.finderBelow,
          'select-top': !this.finderBelow
        }
      },
      availableChoices () {
        const term = this.currentSearch.toLowerCase()
        const filter = this.filter === false || isFunction(this.filter) ? this.filter : defaultFilter
        return isFunction(filter)
          ? this.choices.filter(choice => filter(term, choice, defaultFilter))
          : this.choices
      },
      componentId () {
        return {
          wrapper: `${this.id}-wrapper`,
          search: `${this.id}-search`
        }
      },
      currentChoice () {
        return find(this.choices, matches({value: this.currentValue})) || this.defaultChoice
      },
      currentChoiceIndex () {
        return findIndex(this.choices, matches({value: this.currentValue}))
      },
      isDismissable () {
        return this.currentChoice && this.defaultValue !== null && this.currentChoice !== this.defaultChoice
      },
      decoratorStyle () {
        return {minHeight: `calc(${this.size}px - 1rem)`}
      }
    },
    watch: {
      currentValue (value) {
        setTimeout(() => {
          this.$emit('input', value)
          this.$emit('choice', this.currentChoice)
          this.updateSize()
        }, 0)
      }
    },
    created () {
      this.currentValue = this.value || null
      this.resizeListener = throttle(this.updateSize, 250)
      this.scrollListener = throttle(this.updateFinderPosition, 250)
    },
    mounted () {
      this.updateSize()
      this.updateFinderPosition()
      window.addEventListener('resize', this.resizeListener)
      window.addEventListener('scroll', this.scrollListener, { passive: true })
    },
    beforeDestroy () {
      window.removeEventListener('resize', this.resizeListener)
      window.removeEventListener('scroll', this.scrollListener)
    },
    methods: {
      toggleFinder (focus = true, forcedState = null) {
        const currentState = this.showFinder
        const newState = forcedState === null ? !this.showFinder : forcedState

        if (currentState === newState) return

        this.showFinder = newState
        this.currentSearch = ''

        if (focus && newState && this.$refs.search) {
          setTimeout(() => this.$refs.search.focus(), 0)
        } else if (focus && newState && this.$refs.choices.firstChild) {
          setTimeout(() => this.$refs.choices.firstChild.focus(), 0)
        } else if (focus && !newState && this.$refs.current) {
          setTimeout(() => this.$refs.current.focus(), 0)
        }
      },
      openFinder (focus) {
        this.toggleFinder(isBoolean(focus) ? focus : true, true)
      },
      closeFinder (focus) {
        this.toggleFinder(isBoolean(focus) ? focus : true, false)
      },
      maybeSelect () {
        if (this.availableChoices.length === 1) {
          this.currentValue = this.availableChoices[0].value
          this.closeFinder()
        }
      },
      typeSelect (event) {
        if (this.showFinder) return

        const cidx = this.currentChoiceIndex

        // reset type-search timer
        clearTimeout(this.typedTimer)
        this.typedTimer = setTimeout(() => { this.typedSearch = '' }, 500)

        /**
         * emulates basic select features like:
         * * open on enter
         * * up/down navigating choices without opening select
         */
        switch (event.keyCode) {
          case 13: // enter
            this.toggleFinder()
            return
          case 27: // escape
            this.dismissChoice()
            return
          case 38: // up
            event.preventDefault()
            if (cidx > 0) {
              this.currentValue = this.choices[cidx - 1].value
            }
            return
          case 40: // down
            event.preventDefault()
            if (cidx < this.choices.length - 1) {
              this.currentValue = this.choices[cidx + 1].value
            }
            return
        }

        /**
         * event.key is supported in modern browsers
         * and refers to the actual key being pressed
         * this code assumes that every single character
         * key value is a valid character in every language
         *
         * TODO: it would be nice to distinguish between actual
         * character classes instead of string length
         */
        if (event.key && event.key.length === 1) {
          this.typedSearch += event.key
          const term = this.typedSearch.toLowerCase()
          const choice = this.choices.filter(typeFilter.bind(null, term))[0]

          if (choice) {
            this.currentValue = choice.value
          }
        }
      },
      select (choice) {
        if (choice) {
          this.currentValue = choice.value
        }

        this.closeFinder()
      },
      focusChoices () {
        this.$refs.choices.firstChild.focus()
      },
      nextChoice (event) {
        (event.target.nextElementSibling || event.target.parentNode.firstChild).focus()
      },
      prevChoice (event) {
        (event.target.previousElementSibling || event.target.parentNode.lastChild).focus()
      },
      dismissChoice () {
        this.currentValue = this.defaultValue
      },
      dismissSelect () {
        this.closeFinder(false)
      },
      updateSize () {
        this.size = this.$refs.current.clientHeight
      },
      updateFinderPosition () {
        const {current, finder} = this.$refs

        if (!finder || !current) return

        if (finder.offsetHeight > 0) {
          this.finderSize = finder.offsetHeight
        }

        const calendarHeight = this.finderSize || 500
        const inputBounds = current.getBoundingClientRect()
        const inputHeight = current.offsetHeight
        const distanceFromBottom = window.innerHeight - inputBounds.bottom + inputHeight
        this.finderBelow = distanceFromBottom > calendarHeight + 30
      }
    }
  }
</script>
