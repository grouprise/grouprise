<template>
  <div
    class="media"
    :class="{'media-loading': isLoading }"
  >
    <div class="media-image">
      <img
        v-if="image"
        :src="image.preview"
        alt=""
        class="thumbnail thumbnail-square thumbnail-100"
      >
      <div
        v-else
        class="thumbnail thumbnail-square thumbnail-100 thumbnail-placeholder"
      />
    </div>
    <div class="media-content">
      <sg-file-picker
        :accept="['image/png', 'image/gif', 'image/jpeg', 'capture=camera']"
        :disabled="isLoading"
        :multiple="multiple"
        :btn-label="btnLabel"
        :btn-classes="['btn', 'btn-default', 'btn-sm']"
        @input="upload"
      />
      <div
        v-if="help"
        class="help-block"
      >
        {{ help }}
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    props: {
      image: Object,
      multiple: {
        default: false,
        type: Boolean
      },
      uploader: {
        required: true,
        type: Object
      },
      help: String
    },
    data () {
      return {
        progress: null
      }
    },
    computed: {
      isLoading () {
        return this.progress !== null
      },
      btnLabel () {
        return this.image ? 'Austauschen' : 'Hinzufügen'
      }
    },
    methods: {
      upload (files) {
        this.progress = 0
        this.uploader.upload(files, progress => { this.progress = progress.complete })
          .then(files => {
            this.progress = null
            this.$emit('input', files)
          })
          .catch(files => {
            this.progress = null
            this.$emit('input', null)
          })
      }
    }
  }
</script>
