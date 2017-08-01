<template>
  <div class="group-preview">
    <header class="group-preview-header">
      <div class="group-preview-image" :class="{'group-preview-image-placeholder': !group.cover}">
        <img :src="group.cover" v-if="group.cover" alt="">
      </div>
      <div class="avatar-wrap group-avatar">
        <sg-avatar :size="64" :entity="group"></sg-avatar>
      </div>
    </header>
    <div class="group-preview-body">
      <h3>{{ group.name }}</h3>
      <p>{{ group.description }}</p>
    </div>
  </div>
</template>

<script>
  export default {
    props: {
      group: Object
    }
  }
</script>
