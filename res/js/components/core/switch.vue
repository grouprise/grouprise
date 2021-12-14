<template>
  <label class="switch-wrap">
    <span class="switch-description">{{ label }}</span>

    <button
      type="button"
      class="switch"
      role="checkbox"
      :class="{'switch-active': currentValue }"
      :data-true="trueLabel"
      :data-false="falseLabel"
      :aria-checked="currentValue ? 'true' : 'false'"
      @click="toggle"
    >
      <span class="switch-trigger" />
      <transition>
        <span
          v-if="currentValue"
          key="label-on"
          class="switch-label switch-label-on"
        >{{ trueLabel }}</span>
        <span
          v-else
          key="label-off"
          class="switch-label switch-label-off"
        >{{ falseLabel }}</span>
      </transition>
    </button>
  </label>
</template>

<script>
  export default {
    name: 'GroupriseSwitch',
    props: {
      trueLabel: {
        type: String,
        default: 'An'
      },
      falseLabel: {
        type: String,
        default: 'Aus'
      },
      label: String,
      value: {
        type: Boolean,
        required: true
      }
    },
    data () {
      return {
        currentValue: false
      }
    },
    watch: {
      currentValue (value) {
        setTimeout(() => { this.$emit('input', value) }, 0)
      }
    },
    created () {
      this.currentValue = !!this.value
    },
    methods: {
      toggle () {
        this.currentValue = !this.currentValue
      }
    }
  }
</script>
