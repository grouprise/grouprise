<template>
  <div class="content-list">
    <span v-if="loading">Lade ...</span>
    <div>
      <select v-model="filters.type" @change="updateFilters">
        <option value="">Alle Beiträge</option>
        <option value="articles">Nur Artikel</option>
        <option value="upcoming-events">Kommende Veranstaltungen</option>
      </select>
    </div>
    <ol class="content-preview-list">
      <li v-for="association in objectList" :key="association.id">
        <content-preview :association="association"/>
      </li>
    </ol>
    <div v-if="nextPageURL" class="btn-toolbar btn-toolbar-centered">
      <button @click="loadMore" class="btn btn-default">Weitere Beiträge</button>
    </div>
  </div>
</template>

<script>
  import ContentPreview from '../preview/content-preview.vue'
  import ListMixin from './list-mixin'
  export default {
    mixins: [ListMixin],
    components: {
      ContentPreview
    },
    data () {
      return {
        filters: {
          type: '',
          ordering: '-pub_time'
        }
      }
    },
    methods: {
      updateFilters () {
        // auto-ordering
        if (this.filters.type === 'upcoming-events') {
          this.filters.ordering = 'ev_time'
        } else {
          this.filters.ordering = '-pub_time'
        }

        this.loadInitial('/stadt/api/content?')
      }
    },
    created () {
      this.updateFilters()
    }
  }
</script>
