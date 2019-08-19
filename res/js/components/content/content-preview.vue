<template>
  <article class="content-preview">
    <a :href="association.url" class="content-preview-body">
      <div class="content-preview-text">
        <div class="content-preview-header">
          <h3 class="content-title">
            {{ association.title }}
          </h3>
        </div>
      </div>
    </a>
  </article>
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
