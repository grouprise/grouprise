<template>
  <div class="content-meta">
    <div class="content-meta-avatar">
      <div class="avatar avatar-size-48-48" style="color: inherit">
        <i class="fa" style="font-size: 2.25rem" :class="choice.icon"></i>
      </div>
    </div>
    <div class="content-meta-info">
      <div class="content-meta-author">{{ choice.name }}</div>
      <div class="content-meta-extra">{{ choice.description }}</div>
    </div>
  </div>
</template>

<script>
  export default {
    props: {
      choice: Object
    }
  }
</script>
