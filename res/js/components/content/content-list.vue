<template>
  <div>
    <ol>
      <li v-for="association in associations" :key="association.id">
        {{ association.title }}
      </li>
    </ol>
  </div>
</template>

<script>
  export default {
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
  }
</script>
