<template>
  <div
    class="gallery-editor"
    :class="{'gallery-editor-uploading': isLoading}"
  >
    <header class="gallery-header">
      <h4>
        <span v-if="imagesReady">{{ imageCount }}</span>
        <span v-else>Lade Bilddaten</span>
        <small>Bilder werden hochgeladen ({{ progress | percent }} %)</small>
      </h4>
      <div
        v-if="isLoading"
        class="gallery-progress"
        :style="loaderStyle"
      />
      <div v-if="imagesReady">
        <sg-file-picker
          :accept="['image/png', 'image/gif', 'image/jpeg', 'capture=camera']"
          :disabled="isLoading"
          :multiple="true"
          @input="upload"
        />
      </div>
      <div
        v-else
        class="spinner"
      />
    </header>
    <div
      v-if="imagesReady"
      class="gallery-container"
    >
      <table class="table table-flex table-striped">
        <tbody>
          <tr
            v-for="image in images"
            :key="image.id"
          >
            <td>
              <img
                :src="image.preview"
                alt=""
              >
            </td>
            <td class="table-align-left">
              {{ image.label }}
            </td>
            <td>
              <button
                class="btn btn-danger btn-icon btn-sm"
                type="button"
                @click="remove(image)"
              >
                <i class="sg sg-remove" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
  import UploaderFactory from '../../util/uploader'
  import { image } from '../../adapters/api'
  import { danger } from '../../util/notify'

  const uploader = UploaderFactory(image)

  export default {
    filters: {
      percent (value) {
        return new Intl.NumberFormat('de-DE', {
          maximumFractionDigits: 0
        }).format(value)
      }
    },
    props: {
      images: Array,
      imagesReady: {
        type: Boolean,
        default: true
      }
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
      loaderStyle () {
        return this.isLoading
          ? { transform: `scaleX(${this.progress / 100})` }
          : {}
      },
      imageCount () {
        return this.images.length === 0
          ? 'Keine Bilder in der Galerie'
          : this.images.length === 1
            ? `Ein Bild in der Galerie`
            : `${this.images.length} Bilder in der Galerie`
      }
    },
    methods: {
      upload (files) {
        this.progress = 0
        uploader.upload(files, progress => { this.progress = progress.complete }, 'allSettled')
          .then(results => {
            this.progress = null
            const files = results
              .filter(r => r.status === 'fulfilled')
              .map(r => r.value)

            if (files.length > 0) {
              this.$emit('add', files)
            }

            if (files.length !== results.length) {
              danger(`Einige Dateien konnten nicht hochgeladen werden. Waren sie zu groß?`)
            }
          })
      },
      remove (file) {
        this.$emit('remove', file)
      }
    }
  }
</script>
