<template>
  <LMap
    ref="map"
    :style="{ height, width: '100%' }"
    :zoom="zoom"
    :center="center"
    :min-zoom="realMinZoom"
    :max-bounds="maxBounds"
    @update:zoom="zoom = $event"
    @update:center="center = $event"
    @update:bounds="bounds = $event"
    v-on="$listeners"
  >
    <LTileLayer
      :url="tileServer.url"
      :attribution="tileServer.attribution"
      :detect-retina="true"
      :bounds="maxBounds"
    />
    <slot />
  </LMap>
</template>

<script>
  import { LMap, LTileLayer } from 'vue2-leaflet'
  import { LatLngToBounds } from 'app/components/geo/common'

  export default {
    name: 'GroupriseMap',
    components: {LMap, LTileLayer},
    props: {
      tileServer: {
        type: Object,
        default: () => window.app.conf.geo.tileServer
      },
      initialCenter: {
        type: Array,
        default: () => window.app.conf.geo.initialCenter
      },
      initialZoom: {
        type: Number,
        default: () => window.app.conf.geo.initialZoom
      },
      height: {
        type: String,
        default: '300px'
      },
      maxBounds: {
        type: Object,
        default: null,
      },
      minZoom: {
        type: Number,
        default: null,
      }
    },
    data () {
      return {
        zoom: this.initialZoom,
        center: [0, 0],
        bounds: null
      }
    },
    computed: {
      realMinZoom () {
        if (this.minZoom !== null) return this.minZoom
        if (this.maxBounds !== null) {
          const map = this.$refs.map?.mapObject
          if (map) return map.getBoundsZoom(this.maxBounds)
        }
        return null
      }
    },
    async mounted () {
      await this.$nextTick()
      this.setPosition(this.initialCenter)
    },
    methods: {
      setPosition (points, fitBoundOptions = null) {
        this.$refs.map.mapObject.fitBounds(
          LatLngToBounds(...points),
          {
            maxZoom: isNaN(this.initialZoom) ? null : this.initialZoom,
            ...(fitBoundOptions ?? {})
          }
        )
      }
    }
  }
</script>
