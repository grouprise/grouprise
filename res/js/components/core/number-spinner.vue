<template>
  <div class="numspi">
    <div class="numspi-inner">
      <div class="numspi-ctl">
        <button type="button" class="numspi-btn" @click="modifyValue(-1)" :disabled="!allowDecrement">
          <i class="sg sg-decrease"></i>
        </button>
        <input class="numspi-input" type="number" :min="min" :max="max" :step="step" v-model.number="currentValue" :id="id">
        <button type="button" class="numspi-btn" @click="modifyValue(1)" :disabled="!allowIncrement">
          <i class="sg sg-increase"></i>
        </button>
      </div>
    </div>
    <label class="numspi-label" :for="id">{{ label }}</label>
  </div>
</template>

<script>
  import randomId from 'random-id'
  const stepValue = step => typeof step === 'number' ? step : 1

  export default {
    props: {
      value: {
        type: Number,
        default: 0
      },
      step: {
        type: [Number, String],
        default: 1
      },
      min: {
        type: Number,
        default: null
      },
      max: {
        type: Number,
        default: null
      },
      label: String
    },
    data () {
      return {
        currentValue: 1,
        id: randomId(20, 'a')
      }
    },
    computed: {
      allowIncrement () {
        return this.max === null || this.currentValue + stepValue(this.step) <= this.max
      },
      allowDecrement () {
        return this.min === null || this.currentValue - stepValue(this.step) >= this.min
      }
    },
    methods: {
      modifyValue (modifier) {
        this.currentValue += stepValue(this.step) * modifier
      }
    },
    created () {
      this.currentValue = this.value || null
    },
    watch: {
      currentValue (value) {
        setTimeout(() => { this.$emit('input', value) }, 0)
      }
    }
  }
</script>
