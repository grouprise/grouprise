<template>
  <div>
    <span v-if="loading">Lade ...</span>
    <div>
      <label>
        <input type="checkbox" v-model="filters.membership" @change="updateFilters">
        Mitglied
      </label>
      <label>
        <input type="checkbox" v-model="filters.subscription" @change="updateFilters">
        Abonnent
      </label>
      <select v-model="filters.ordering" @change="updateFilters">
        <option value="-activity">Aktivität</option>
        <option value="name">Name</option>
      </select>
    </div>
    <ol class="groups">
      <li v-for="group in objectList" :key="group.id">
        <group-preview :group="group"/>
      </li>
    </ol>
    <div v-if="nextPageURL" class="btn-toolbar btn-toolbar-centered">
      <button @click="loadMore" class="btn btn-default">Weitere Gruppen</button>
    </div>
  </div>
</template>

<script>
  import GroupPreview from '../preview/group-preview.vue'
  import ListMixin from './list-mixin'
  export default {
    mixins: [ListMixin],
    components: {
      GroupPreview
    },
    data () {
      return {
        filters: {
          membership: false,
          subscription: false,
          ordering: '-activity'
        }
      }
    },
    methods: {
      updateFilters () {
        this.loadInitial('/stadt/api/groups?page_size=10&')
      }
    },
    created () {
      this.updateFilters()
    }
  }
</script>
