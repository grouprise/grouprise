<template>
  <div>
    <div>
      <select v-model="filters.type" v-on:change="updateFilters">
        <option value="">Alle Beiträge</option>
        <option value="articles">Nur Artikel</option>
        <option value="upcoming-events">Kommende Veranstaltungen</option>
      </select>
    </div>
    <ol class="groups">
      <li v-for="group in groups" :key="group.id">
        <group-preview :group="group"/>
      </li>
    </ol>
    <div v-if="nextPageURL" class="btn-toolbar btn-toolbar-centered">
      <button v-on:click="loadMore" class="btn btn-default">Weitere Gruppen</button>
    </div>
  </div>
</template>

<script>
  import GroupPreview from './group-preview.vue'
  export default {
    components: {
      GroupPreview
    },
    data () {
      return {
        filters: {
          type: '',
          ordering: '-pub_time'
        },
        groups: [],
        nextPageURL: null
      }
    },
    methods: {
      load (url, groups) {
        fetch(url)
          .then(res => res.json())
          .then(paginator => {
            this.groups = groups.concat(paginator.results)
            this.nextPageURL = paginator.next
          })
      },
      loadMore () {
        this.load(this.nextPageURL, this.groups)
      },
      updateFilters () {
        // reload content list with filter params
        let params = new URLSearchParams()
        Object.entries(this.filters).forEach(([k, v]) => params.set(k, v))
        this.load('/stadt/api/groups?page_size=10&' + params, [])
      }
    },
    created () {
      this.updateFilters()
    }
  }
</script>
