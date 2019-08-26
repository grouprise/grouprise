<template>
  <div class="content-list">
    <div>
      <select v-model="filters.type" v-on:change="updateFilters">
        <option value="">Alle Beiträge</option>
        <option value="articles">Nur Artikel</option>
        <option value="upcoming-events">Kommende Veranstaltungen</option>
      </select>
    </div>
    <ol class="content-preview-list">
      <li v-for="association in associations" :key="association.id">
        <content-preview :association="association"/>
      </li>
    </ol>
    <div v-if="nextPageURL" class="btn-toolbar btn-toolbar-centered">
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
    data () {
      return {
        filters: {
          type: '',
          ordering: '-pub_time'
        },
        associations: [],
        nextPageURL: null
      }
    },
    methods: {
      load (url, associations) {
        fetch(url)
          .then(res => res.json())
          .then(paginator => {
            this.associations = associations.concat(paginator.results)
            this.nextPageURL = paginator.next
          })
      },
      loadMore () {
        this.load(this.nextPageURL, this.associations)
      },
      updateFilters () {
        // auto-ordering
        if (this.filters.type == 'upcoming-events')
          this.filters.ordering = 'ev_time'
        else
          this.filters.ordering = '-pub_time'

        // reload content list with filter params
        let params = new URLSearchParams()
        Object.entries(this.filters).forEach(([k, v]) => params.set(k, v))
        this.load('/stadt/api/content?' + params, [])
      }
    },
    created () {
      this.updateFilters()
    }
  }
</script>
