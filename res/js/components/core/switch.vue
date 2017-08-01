<template>
  <label class="switch-wrap">
    <span class="switch-description">{{ label }}</span>

    <button type="button" class="switch" role="checkbox" @click="toggle" :class="{'switch-active': currentValue }"
            :data-true="trueLabel" :data-false="falseLabel" :aria-checked="currentValue ? 'true' : 'false'">
      <span class="switch-trigger"></span>
      <transition >
        <span class="switch-label switch-label-on" key="label-on" v-if="currentValue">{{ trueLabel }}</span>
        <span class="switch-label switch-label-off" key="label-off" v-else>{{ falseLabel }}</span>
      </transition>
    </button>
  </label>
</template>

<script>
  export default {
    props: {
      trueLabel: {
        type: String,
        default: "An"
      },
      falseLabel: {
        type: String,
        default: "Aus"
      },
      label: String,
      value: {
        type: Boolean,
        required: true
      }
    },
    data() {
      return {
        currentValue: false
      }
    },
    methods: {
      toggle() {
        this.currentValue = !this.currentValue
      }
    },
    created() {
      this.currentValue = !!this.value
    },
    watch: {
      currentValue(value) {
        setTimeout(() => this.$emit("input", value), 0)
      }
    }
  }
</script>
