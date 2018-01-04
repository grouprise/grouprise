<template>
    <div class="avatar-wrap">
        <div class="avatar" :title="entity.name" :class="avatarClasses" v-if="entity.avatar !== null">
            <img :src="entity.avatar" alt="">
        </div>
        <div class="avatar avatar-initials" :title="entity.name" :class="avatarClasses" :data-initials="entity.initials.length" :style="avatarStyle" v-else>
          <span v-if="entity.initials.length <= 4">
            {{ entity.initials }}
          </span>
          <span v-else>
            {{ entity.initials.substr(0, 1) }}...
          </span>
        </div>
    </div>
</template>

<script>
  export default {
    props: {
      entity: Object,
      size: {
        type: Number,
        default: 48
      }
    },
    computed: {
      avatarClasses () {
        return [`avatar-size-${this.size}-${this.size}`]
      },
      avatarStyle () {
        return {
          backgroundColor: this.entity.avatar_color
        }
      }
    }
  }
</script>
