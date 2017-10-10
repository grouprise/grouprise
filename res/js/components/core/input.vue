<template>
  <div class="form-group" :class="_groupClasses">
    <label class="control-label" :for="id" v-if="label">{{ label }}</label>
    <input class="form-control vue-input" :class="inputClasses" :id="id" v-model="currentValue"
           ref="input"
           @focus="hasFocus = true; hadFocus = true" @blur="hasFocus = false"
           @input="hasChanged = true">
  </div>
</template>

<script>
  import randomId from 'random-id'

  export default {
    props: {
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
    created () {
      this.currentValue = this.value || ''
    },
    mounted () {
      this.$refs.input.type = this.type
    },
    watch: {
      currentValue (value) {
        setTimeout(() => { this.$emit('input', value) }, 0)
      }
    }
  }
</script>
