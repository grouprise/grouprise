<template>
  <div
    class="form-group"
    :class="_groupClasses"
  >
    <label
      v-if="label"
      class="control-label"
      :for="id"
    >{{ label }}</label>
    <input
      :id="id"
      ref="input"
      v-model="currentValue"
      class="form-control vue-input"
      :class="inputClasses"
      @focus="hasFocus = true; hadFocus = true"
      @blur="hasFocus = false"
      @input="hasChanged = true"
    >
  </div>
</template>

<script>
  import randomId from 'random-id'

  export default {
    props: {
      value: String,
      type: {
        type: String,
        default: 'text'
      },
      inputClasses: {
        type: [Object, Array, String],
        default: () => []
      },
      groupClasses: {
        type: [Object, Array, String],
        default: () => []
      },
      label: {
        type: String,
        default: null
      }
    },
    data () {
      return {
        currentValue: '',
        id: randomId(20, 'a'),
        hasFocus: false,
        hadFocus: false,
        hasChanged: false
      }
    },
    computed: {
      _groupClasses () {
        return [this.groupClasses, {
          'input-filled': Boolean(this.currentValue),
          'input-empty': Boolean(!this.currentValue),
          'input-changed': this.hasChanged,
          'input-focused': this.hasFocus,
          'input-had-focus': this.hadFocus,
          'input-blurred': !this.hasFocus
        }, `input-type-${this.type.toLowerCase()}`]
      }
    },
    watch: {
      currentValue (value) {
        setTimeout(() => { this.$emit('input', value) }, 0)
      }
    },
    created () {
      this.currentValue = this.value || ''
    },
    mounted () {
      this.$refs.input.type = this.type
    }
  }
</script>
