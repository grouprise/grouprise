<template>
  <div class="content-list">
    <div>
      <select v-model="filters.type" v-on:change="updateFilters">
        <option value="">Alle</option>
        <option value="articles">Artikel</option>
        <option value="events">Veranstaltungen</option>
      </select>
    </div>
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
        filters: {
          type: '',
        },
        associations: [],
        nextPageURL: null,
      }
    },
    methods: {
      load(url) {
        fetch(url)
          .then(res => res.json())
          .then(paginator => {
            this.associations = this.associations.concat(paginator.results)
            this.nextPageURL = paginator.next
          })
      },
      loadMore() {
        this.load(this.nextPageURL)
      },
      updateFilters() {
        let params = new URLSearchParams()
        Object.entries(this.filters).forEach(([k, v]) => params.set(k, v))
        this.associations = []
        this.load('/stadt/api/content?' + params)
      },
    },
    created() {
      this.updateFilters()
    }
  }
</script>
