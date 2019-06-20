<template>
  <div>
    <ol>
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
          {
            id: 1,
            title: 'Erster Eintrag',
          },
          {
            id: 2,
            title: 'Zweiter Eintrag',
          },
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
