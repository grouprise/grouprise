<template>
  <LMap
    ref="map"
    :style="{ height, width: '100%' }"
    :zoom="zoom"
    :center="center"
    @update:zoom="zoom = $event"
    @update:center="center = $event"
    @update:bounds="bounds = $event"
    v-on="$listeners"
  >
    <LTileLayer
      :url="tileServer.url"
      :attribution="tileServer.attribution"
      :detect-retina="true"
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
      }
    },
    data () {
      return {
        zoom: this.initialZoom,
        center: [0, 0],
        bounds: null
      }
    },
    mounted () {
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
