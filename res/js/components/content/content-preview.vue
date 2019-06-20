<template>
  <div>
    {{ association.title }}
  </div>
</template>

<script>
  export default {
    props: {
      association: {
        type: Object,
        required: true
      }
    }
  }
</script>
