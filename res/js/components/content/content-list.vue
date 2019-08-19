<template>
  <div class="content-list">
    <ol class="content-preview-list">
      <li v-for="association in associations" :key="association.id">
        <content-preview :association="association"/>
      </li>
    </ol>
    <div class="btn-toolbar btn-toolbar-centered">
      <button v-on:click="loadMore" class="btn btn-default">Weitere Beiträge</button>
    </div>
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
        associations: [],
        next_page_url: '/stadt/api/content',
      }
    },
    methods: {
      loadMore() {
        fetch(this.next_page_url)
          .then(res => res.json())
          .then(paginator => {
            this.associations = this.associations.concat(paginator.results)
            this.next_page_url = paginator.next
          })
      },
    },
    created() {
      this.loadMore()
    }
  }
</script>
