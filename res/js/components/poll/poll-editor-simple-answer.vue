<template>
  <sg-input
    v-model="answer.title"
    label="Antwort"
  />
</template>

<script>
  export default {
    model: {
      prop: 'answer'
    },
    props: {
      answer: Object
    }
  }
</script>
