<template>
  <div>
    <button
      type="button"
      :class="btnClasses"
      :disabled="disabled"
      @click.prevent="open"
    >
      <i
        class="sg"
        :class="btnIcon"
      /> {{ btnLabel }}
    </button>
    <input
      ref="input"
      type="file"
      :accept="accept.join(',')"
      :multiple="multiple"
      style="position: absolute; z-index: -1; opacity: 0; pointer-events: none; height: 0; width: 0"
      @change="dispatch"
    >
  </div>
</template>

<script>
  export default {
    props: {
      accept: Array,
      multiple: Boolean,
      disabled: {
        type: Boolean,
        default: () => false
      },
      btnClasses: {
        type: [Array, Object],
        default: () => ['btn', 'btn-link', 'btn-sm']
      },
      btnIcon: {
        type: [Array, Object],
        default: () => ['sg', 'sg-add']
      },
      btnLabel: {
        type: String,
        default: () => 'Hinzufügen'
      }
    },
    methods: {
      open () {
        this.$refs.input.click()
      },
      dispatch (e) {
        this.$emit('input', [].slice.call(e.target.files))
      }
    }
  }
</script>
