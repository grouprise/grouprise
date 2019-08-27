<template>
  <article class="content-preview">
    <a :href="group.url" class="content-preview-body">
      <div class="content-preview-text">
        <div class="content-preview-header">
          <h3 class="content-title">
            {{ group.name }}
          </h3>
        </div>
      </div>
    </a>
  </article>
</template>

<script>
  export default {
    props: {
      group: {
        type: Object,
        required: true
      }
    }
  }
</script>
