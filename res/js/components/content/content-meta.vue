<template>
    <div class="content-meta">
        <div class="content-meta-avatar">
            <sg-avatar :entity="choice"></sg-avatar>
        </div>
        <div class="content-meta-info">
            <div class="content-meta-author">{{ choice.name }}</div>
            <div class="content-meta-extra" v-if="choice.tags">{{ tags }}</div>
        </div>
    </div>
</template>

<script>
  export default {
    props: {
      choice: {
        choice: Object,
        required: true
      }
    },
    computed: {
      tags () {
        return (this.choice.tags || []).map(tag => `#${tag.name}`).join(', ')
      }
    }
  }
</script>
