<template>
  <sg-user :user="user" v-if="user" v-bind="userAttribs">
    <div class="form-modern" v-if="allowEdit || displayLogin"
         style="display: flex; align-items: center">
      <sg-input v-model="username" label="Dein Name" style="margin: 0" v-if="allowEdit" />
      <a :href="loginUrl" class="btn btn-link" v-if="displayLogin">Anmelden</a>
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
        return this.userModel === 'anonymous' && this.anonymousLogin
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
    async created () {
      this.userModel = await getCurrentUser()
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
    }
  }
</script>
