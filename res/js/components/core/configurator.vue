<template>
  <div
    ref="configurator"
    class="configurator"
  >
    <div
      class="configurator-label"
      tabindex="0"
      @click.stop="toggle(true)"
      @keydown.enter="toggle()"
      @focus="toggle(true)"
    >
      <slot name="label" />
    </div>
    <transition name="fade-down">
      <div
        v-if="opened"
        v-on-click-outside="dismiss"
        class="configurator-popup"
      >
        <header class="configurator-header">
          <slot name="icon" />
          <h3 class="configurator-title">
            <slot name="title" />
          </h3>
          <div class="configurator-modifiers">
            <slot name="modifiers" />
          </div>
        </header>
        <div class="configurator-body">
          <slot />
        </div>
        <footer class="configurator-footer">
          <slot name="footer">
            <div class="btn-toolbar btn-toolbar-right">
              <slot name="actions">
                <button
                  type="button"
                  class="btn btn-link btn-sm"
                  @click="abort"
                >
                  Abbrechen
                </button>
                <button
                  type="button"
                  class="btn btn-primary btn-sm"
                  @click="save"
                >
                  Speichern
                </button>
              </slot>
            </div>
          </slot>
        </footer>
      </div>
    </transition>
  </div>
</template>

<script>
  import { mixin as onClickOutside } from 'vue-on-click-outside'
  import { on } from 'luett'
  import { SingletonListener } from '../../util/events'

  const focusInListener = SingletonListener(
    callback => on(document, 'focusin', callback),
    (event, self) => {
      if (self.opened && !self.$el.contains(event.target)) {
        self.toggle(false)
      }
    }
  )

  export default {
    name: 'GroupriseConfigurator',
    mixins: [onClickOutside],
    data () {
      return {
        opened: false
      }
    },
    mounted () {
      focusInListener.register(this)
    },
    beforeDestroy () {
      focusInListener.remove(this)
    },
    methods: {
      dismiss () {
        this.abort()
      },
      abort () {
        this.$emit('abort')
        this.toggle(false)
      },
      save () {
        this.$emit('save')
        this.toggle(false)
      },
      toggle (force = null) {
        const newState = force !== null ? force : !this.opened
        if (newState !== this.opened) {
          this.$emit(newState ? 'show' : 'hide')
          this.opened = newState
        }
      }
    }
  }
</script>
