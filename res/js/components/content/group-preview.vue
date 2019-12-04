<template>
  <transition name="fade-down">
    <div
      v-show="showPreview"
      class="group-preview"
      @mouseenter="setHovered(true)"
      @mouseleave="setHovered(false)"
    >
      <header class="group-preview-header">
        <div
          class="group-preview-image"
          :class="{'group-preview-image-placeholder': !group.cover}"
        >
          <img
            v-if="group.cover"
            :src="group.cover"
            alt=""
          >
        </div>
        <div class="avatar-wrap group-avatar">
          <sg-avatar
            :size="64"
            :entity="group"
          />
        </div>
      </header>
      <div class="group-preview-body">
        <h3>{{ group.name }}</h3>
        <p>{{ group.description }}</p>
      </div>
    </div>
  </transition>
</template>

<script>
  export default {
    props: {
      group: Object,
      visibilityDelay: {
        type: Number,
        default: 250
      },
      visible: {
        type: Boolean,
        default: true
      }
    },
    data () {
      return {
        isHovered: false,
        isHoveredDelay: null
      }
    },
    computed: {
      showPreview () {
        return this.visible || this.isHovered
      }
    },
    methods: {
      setHovered (value) {
        if (value) {
          clearTimeout(this.isHoveredDelay)
          this.isHovered = true
        } else {
          this.isHoveredDelay = setTimeout(() => { this.isHovered = false }, this.visibilityDelay)
        }
      }
    }
  }
</script>
