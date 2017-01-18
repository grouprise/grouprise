<template>
    <div class="select" :id="componentId.wrapper" :class="{'select-open': showFinder}" @keydown.esc="closeFinder" v-on-clickaway="dismissSelect">
        <div class="select-current" @click.prevent="toggleFinder()" @keydown="typeSelect" tabindex="0" ref="current">
            <slot name="current-choice">
                <component :is="renderer" :choice="currentChoice" v-if="currentChoice"></component>
            </slot>
            <slot name="no-result">
                <div class="select-default" v-if="!currentChoice">
                    {{ texts.noSelection }}
                </div>
            </slot>
            <div class="select-decorator select-dismiss" :style="decoratorStyle" v-if="isDismissable" @click.prevent.stop="dismissChoice">
                <i>×</i>
            </div>
            <div class="select-decorator select-caret" :style="decoratorStyle" v-else>
                <i>▼</i>
            </div>
        </div>
        <transition name="fade">
            <div class="select-finder" v-show="showFinder">
                <div class="select-search" v-if="filter && choices.length > searchThreshold">
                    <label :for="componentId.search" class="sr-only">{{ texts.searchLabel }}</label>
                    <input type="search" class="select-search-input" v-model="currentSearch" ref="search"
                           :id="componentId.search" :placeholder="texts.searchPlaceholder"
                           @keydown.down.prevent="focusChoices" @keydown.enter.prevent>
                    <span class="select-search-count">{{ availableChoices.length }}</span>
                </div>

                <ol class="select-choices" @keydown.up.prevent="prevChoice" @keydown.down.prevent="nextChoice"
                    ref="choices" v-if="availableChoices.length > 0">
                    <li v-for="(choice, index) in availableChoices" :data-value="choice.value" @click="select"
                        @keydown.enter="select" tabindex="0">
                        <slot name="choice">
                            <component :is="renderer" :choice="choice" :index="index"></component>
                        </slot>
                    </li>
                </ol>
                <p class="select-no-results" v-else>{{ texts.noResult }}</p>
            </div>
        </transition>
    </div>
</template>

<script>
    import { mixin as clickaway } from 'vue-clickaway'
    import { includes, find, findIndex, isFunction, isBoolean, throttle } from 'lodash'
    import uuid from 'uuid'

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
        name: 'select',
        mixins: [clickaway],
        props: {
            id: {
                type: String,
                default: () => uuid.v1()
            },
            texts: {
                type: Object,
                default: () => ({
                    searchPlaceholder: "Suche nach Einträgen",
                    searchLabel: "Suche",
                    noResult: "Keine Ergebnisse gefunden 😔",
                    noSelection: "Keine Auswahl"
                })
            },
            renderer: Object,
            defaultValue: [String, Number],
            defaultChoice: Object,
            initialValue: {
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
        data() {
            return {
                value: null,
                showFinder: false,
                currentSearch: "",
                typedSearch: "",
                typedTimer: null,
                size: 0,
                resizeListener: null
            }
        },
        computed: {
            availableChoices() {
                const term = this.currentSearch.toLowerCase()
                const filter = this.filter === false || isFunction(this.filter) ? this.filter : defaultFilter
                return isFunction(filter)
                    ? this.choices.filter(choice => filter(term, choice, defaultFilter))
                    : this.choices
            },
            componentId() {
                const id = this.id || this._uid
                return {
                    wrapper: `${id}-wrapper`,
                    search: `${id}-search`
                }
            },
            currentChoice() {
                return find(this.choices, {value: this.value}) || this.defaultChoice
            },
            currentChoiceIndex() {
                return findIndex(this.choices, {value: this.value})
            },
            isDismissable() {
                return this.currentChoice && this.defaultValue !== null && this.currentChoice !== this.defaultChoice
            },
            decoratorStyle() {
                return {minHeight: `calc(${this.size}px - 1rem)`}
            }
        },
        methods: {
            toggleFinder(focus = true, forcedState = null) {
                const currentState = this.showFinder
                const newState = forcedState === null ? !this.showFinder : forcedState

                if (currentState === newState) return;

                this.showFinder = newState
                this.currentSearch = ""

                if (focus && newState && this.$refs.search) {
                    setTimeout(() => this.$refs.search.focus(), 0)
                } else if (focus && newState && this.$refs.choices.firstChild) {
                    setTimeout(() => this.$refs.choices.firstChild.focus(), 0)
                } else if (focus && !newState && this.$refs.current) {
                    setTimeout(() => this.$refs.current.focus(), 0)
                }
            },
            openFinder(focus) {
                this.toggleFinder(isBoolean(focus) ? focus : true, true)
            },
            closeFinder(focus) {
                this.toggleFinder(isBoolean(focus) ? focus : true, false)
            },
            typeSelect(event) {
                if (this.showFinder) return;

                const cidx = this.currentChoiceIndex

                // reset type-search timer
                clearTimeout(this.typedTimer)
                this.typedTimer = setTimeout(() => this.typedSearch = "", 500)

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
                        event.preventDefault();
                        if (cidx > 0) {
                            this.value = this.choices[cidx - 1].value
                        }
                        return
                    case 40: // down
                        event.preventDefault();
                        if (cidx < this.choices.length - 1) {
                            this.value = this.choices[cidx + 1].value
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
                        this.value = choice.value
                    }
                }
            },
            select(event) {
                const target = event.currentTarget || event.target
                const value = target.getAttribute("data-value")
                const choice = find(this.choices, {value})

                if (choice) {
                    this.value = choice.value
                }

                this.closeFinder()
            },
            focusChoices() {
                this.$refs.choices.firstChild.focus()
            },
            nextChoice(event) {
                (event.target.nextElementSibling || event.target.parentNode.firstChild).focus()
            },
            prevChoice(event) {
                (event.target.previousElementSibling || event.target.parentNode.lastChild).focus()
            },
            dismissChoice() {
                this.value = this.defaultValue
            },
            dismissSelect() {
                this.closeFinder(false)
            },
            updateSize() {
                this.size = this.$refs.current.clientHeight
            }
        },
        watch: {
            value: function (value) {
                setTimeout(() => {
                    this.$emit("select", this.currentChoice || value)
                    this.updateSize()
                }, 0)
            }
        },
        created() {
            this.value = this.initialValue || null
            this.resizeListener = throttle(this.updateSize, 250)
        },
        mounted() {
            this.updateSize()
            window.addEventListener('resize', this.resizeListener)
        },
        beforeDestroy() {
            window.removeEventListener('resize', this.resizeListener)
        }
    }
</script>

<style scoped>
    .fade-enter-active, .fade-leave-active {
        transition: opacity .2s, transform .2s;
    }

    .fade-enter, .fade-leave-to /* .fade-leave-active in <2.1.8 */
    {
        opacity: 0;
        transform: translateY(-5px);
    }
</style>
