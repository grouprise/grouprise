<template>
  <div class="poll-answer">
    <div class="poll-answer-body">
      <strong class="poll-answer-name">{{ option.title }}</strong>
      <figure
        v-if="option.voters.length > 0"
        class="poll-answer-voters"
      >
        <figcaption>
          <i
            class="sg sg-poll-favorite"
            title="Favorisiert von"
          />
        </figcaption>
        <ul class="avatars avatars-nowrap">
          <li
            v-for="voter in option.voters"
            :key="voter.id"
          >
            <sg-avatar
              :entity="voter"
              :size="16"
              :rounded="true"
              :inline="true"
            />
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
