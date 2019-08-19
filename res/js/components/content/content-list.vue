<template>
  <div>
    <ol class="content-preview-list">
      <li v-for="association in associations" :key="association.id">
        <content-preview :association="association"/>
      </li>
    </ol>
  </div>
</template>

<script>
  import ContentPreview from './content-preview.vue'
  export default {
    components: {
      ContentPreview
    },
    data() {
      return {
        associations: [
        ],
      }
    },
    methods: {
      updateContent() {
        fetch('/stadt/api/content')
          .then(res => res.json())
          .then(data => { this.associations = data })
      }
    },
    created() {
      this.updateContent()
    }
  }
</script>
