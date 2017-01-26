<template>
  <div class="configurator" ref="configurator">
    <div class="configurator-label" @click="toggle()" @keydown.enter="toggle()" tabindex="0">
      <slot name="label"></slot>
    </div>
    <transition name="fade-down">
      <div class="configurator-popup" v-if="opened" v-on-clickaway="dismiss" @mouseenter="setCurrentElement" @mouseleave="setCurrentElement">
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
  import { mixin as clickaway } from 'vue-clickaway'

  export default {
    mixins: [clickaway],
    data() {
      return {
        opened: false,
        isCurrentElement: false
      }
    },
    methods: {
      setCurrentElement(event) {
        this.isCurrentElement = event.type === 'mouseenter'
      },
      dismiss() {
        if(!this.isCurrentElement) {
          this.abort()
        }
      },
      abort() {
        this.$emit("abort")
        this.toggle(false)
      },
      save() {
        this.$emit("save")
        this.toggle(false)
      },
      toggle(force = null) {
        const newState = force !== null ? force : !this.opened
        this.$emit(newState ? 'show' : 'hide')
        this.opened = newState
      }
    }
  }
</script>
