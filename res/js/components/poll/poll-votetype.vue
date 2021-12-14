<template>
  <div class="content-meta">
    <div class="content-meta-avatar">
      <span class="btn-radio-state-indicator" />
    </div>
    <div class="content-meta-info">
      <div class="content-meta-author">
        {{ choice.name }}
      </div>
      <div class="content-meta-extra">
        {{ choice.description }}
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'GrouprisePollVoteType',
    props: {
      choice: Object
    }
  }
</script>
