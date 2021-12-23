<template>
  <div class="poll-answer">
    <slot />
    <button
      type="button"
      class="btn btn-icon btn-sm btn-danger"
      @click="remove"
    >
      <i class="sg sg-remove" />
    </button>
  </div>
</template>

<script>
  export default {
    name: 'GrouprisePollAnswer',
    methods: {
      remove () {
        this.$emit('remove')
      }
    }
  }
</script>
