<template>
  <Map
    ref="map"
    @click="moveLocation"
  >
    <LMarker
      v-if="pointLatLng"
      :lat-lng="pointLatLng"
    />
  </Map>
</template>

<script>
  import { LMarker } from 'vue2-leaflet'
  import { LatLngToWKTPoint, WKTPointToLatLng } from './common'
  import Map from './Map.vue'

  export default {
    name: 'GroupriseLocation',
    components: { Map, LMarker },
    props: {
      point: {
        type: String,
        default: null
      }
    },
    computed: {
      pointLatLng: {
        get () {
          return this.point
            ? WKTPointToLatLng(this.point)
            : null
        },
        set (pointLatLng) {
          this.$emit('input', LatLngToWKTPoint(pointLatLng))
        }
      }
    },
    mounted () {
      if (this.pointLatLng) {
        this.$refs.map.setPosition([this.pointLatLng], { maxZoom: 16 })
      }
    },
    methods: {
      moveLocation ($event) {
        this.pointLatLng = $event.latlng
      }
    }
  }
</script>
