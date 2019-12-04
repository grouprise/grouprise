<template>
  <a
    class="group-media"
    :href="group.url"
  >
    <header class="group-media-image">
      <sg-avatar
        :size="64"
        :entity="group"
      />
    </header>
    <div class="group-media-body">
      <h3>{{ group.name }}</h3>
      <p>{{ group.description|default("Diese Gruppe hat noch keine Beschreibung hinterlegt.")|truncatewords(10) }}</p>
    </div>
  </a>
</template>

<script>
  export default {
    props: {
      group: Object
    }
  }
</script>
