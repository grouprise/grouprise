<template>
  <!-- eslint-disable vue/no-mutating-props -->
  <!-- TODO: fix prop mutation */ -->

  <sg-input
    v-model="answer.title"
    label="Antwort"
  />
</template>

<script>
  export default {
    name: 'GroupriseSimplePollEditorAnswer',
    model: {
      prop: 'answer'
    },
    props: {
      answer: Object
    }
  }
</script>
