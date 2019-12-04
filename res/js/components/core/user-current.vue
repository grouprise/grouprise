<template>
  <sg-user
    v-if="user"
    :user="user"
    v-bind="userAttribs"
  >
    <div
      v-if="allowEdit || displayLogin"
      class="form-modern"
      style="display: flex; align-items: center"
    >
      <sg-input
        v-if="allowEdit"
        v-model="username"
        label="Dein Name"
        style="margin: 0"
      />
      <a
        v-if="displayLogin"
        :href="loginUrl"
        class="btn btn-link"
      >Anmelden</a>
    </div>
  </sg-user>
</template>

<script>
  import { memoize, get } from 'lodash'
  import { gestalt } from '../../adapters/api'
  import { createInitials } from '../../util/strings'
  import randomColor from 'random-color'

  const getCurrentUser = memoize(() => {
    const userId = get(window.app.conf, 'gestalt.id')
    return userId ? gestalt.get(userId) : 'anonymous'
  })

  export default {
    props: {
      anonymousEdit: Boolean,
      anonymousLogin: Boolean,
      userAttribs: Object
    },
    data () {
      return {
        userModel: null,
        username: null,
        anonymousColor: randomColor().hexString()
      }
    },
    computed: {
      loginUrl () {
        return `/stadt/login/?next=${encodeURIComponent(location.pathname)}`
      },
      allowEdit () {
        return this.userModel === 'anonymous' && this.anonymousEdit
      },
      displayLogin () {
        return this.userModel === 'anonymous' && this.anonymousLogin && !this.username
      },
      user () {
        return this.userModel === 'anonymous'
          ? {
            id: null,
            name: this.username,
            initials: createInitials(this.username),
            about: '',
            avatar: null,
            avatar_color: this.anonymousColor,
            url: null
          } : this.userModel
      }
    },
    watch: {
      user () {
        this.$emit('input', this.user)
      },
      username () {
        if (this.username) {
          this.$emit('edit', this.username)
        }
      }
    },
    async created () {
      this.userModel = await getCurrentUser()
    }
  }
</script>
