<template>
  <div class="configurator" ref="configurator">
    <div class="configurator-label" tabindex="0"
         @click.stop="toggle(true)" @keydown.enter="toggle()" @focus="toggle(true)">
      <slot name="label"></slot>
    </div>
    <transition name="fade-down">
      <div class="configurator-popup" v-if="opened" v-on-click-outside="dismiss">
        <header class="configurator-header">
          <slot name="icon"></slot>
          <h3 class="configurator-title">
            <slot name="title"></slot>
          </h3>
          <div class="configurator-modifiers">
            <slot name="modifiers"></slot>
          </div>
        </header>
        <div class="configurator-body">
          <slot></slot>
        </div>
        <footer class="configurator-footer">
          <slot name="footer">
            <div class="btn-toolbar btn-toolbar-right">
              <slot name="actions">
                <button type="button" class="btn btn-link btn-sm" @click="abort">Abbrechen</button>
                <button type="button" class="btn btn-primary btn-sm" @click="save">Speichern</button>
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
    mixins: [onClickOutside],
    data () {
      return {
        opened: false
      }
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
    },
    mounted () {
      focusInListener.register(this)
    },
    beforeDestroy () {
      focusInListener.remove(this)
    }
  }
</script>
