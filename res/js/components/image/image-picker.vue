<template>
  <div class="media" :class="{'media-loading': isLoading }">
    <div class="media-image">
      <img :src="image.preview" alt="" class="thumbnail thumbnail-square thumbnail-100" v-if="image">
      <div class="thumbnail thumbnail-square thumbnail-100 thumbnail-placeholder" v-else></div>
    </div>
    <div class="media-content">
      <sg-file-picker :accept="['image/png', 'image/gif', 'image/jpeg', 'capture=camera']"
                      @input="upload" :disabled="isLoading" :multiple="multiple"
                      :btnLabel="btnLabel"></sg-file-picker>
      <div class="help-block" v-if="help">{{ help }}</div>
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
      }
    }
  }
</script>
