<template>
  <div>
    <div>
      <label>
        <input type="checkbox" v-model="filters.membership" v-on:change="updateFilters">
        Mitglied
      </label>
      <label>
        <input type="checkbox" v-model="filters.subscription" v-on:change="updateFilters">
        Abonnent
      </label>
      <select v-model="filters.ordering" v-on:change="updateFilters">
        <option value="-activity">Aktivität</option>
        <option value="name">Name</option>
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
          membership: false,
          subscription: false,
          ordering: '-activity'
        },
        groups: [],
        nextPageURL: null
      }
    },
    methods: {
      load (url, groups) {
        fetch(url, {credentials: 'same-origin'})
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
