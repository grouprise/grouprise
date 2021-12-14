<template>
  <div class="content-meta content-meta-center">
    <div class="content-meta-avatar">
      <sg-avatar
        :entity="user"
        v-bind="avatarAttribs"
      />
    </div>
    <div class="content-meta-info">
      <slot>
        <div class="content-meta-author">
          <component
            :is="user.url ? 'a' : 'span'"
            :href="user.url"
          >
            {{ user.name }}
          </component>
        </div>
      </slot>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'GroupriseUser',
    props: {
      user: Object,
      avatarAttribs: Object
    }
  }
</script>
