<template>
    <sg-input label="Antwort" v-model="answer.title" />
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
