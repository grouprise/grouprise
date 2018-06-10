<template>
  <div class="poll-answer">
    <div class="poll-answer-body">
      <strong class="poll-answer-name">{{ option.title }}</strong>
      <figure class="poll-answer-voters" v-if="option.voters.length > 0">
        <figcaption>
          <i class="sg sg-poll-favorite" title="Favorisiert von"></i>
        </figcaption>
        <ul class="avatars avatars-nowrap">
          <li v-for="voter in option.voters">
            <sg-avatar :entity="voter" :size="16" :rounded="true" :inline="true" />
          </li>
        </ul>
      </figure>
    </div>
    <div class="poll-answer-actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<script>
  export default {
    props: {
      option: Object
    }
  }
</script>
