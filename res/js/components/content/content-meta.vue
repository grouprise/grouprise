<template>
  <div class="content-meta">
    <div class="content-meta-avatar">
      <sg-avatar :entity="choice" />
    </div>
    <div class="content-meta-info">
      <div class="content-meta-author">
        {{ choice.name }}
      </div>
      <div
        v-if="choice.tags"
        class="content-meta-extra"
      >
        {{ tags }}
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    props: {
      choice: {
        type: Object,
        required: true
      }
    },
    computed: {
      tags () {
        const maxTags = 7
        const tags = (this.choice.tags || []).map(tag => `#${tag.name}`)
        return (
          tags.length > maxTags
            ? tags.slice(0, maxTags).concat('...')
            : tags
        ).join(', ')
      }
    }
  }
</script>
