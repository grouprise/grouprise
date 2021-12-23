<template>
  <Map
    ref="map"
    :height="height"
  >
    <template v-for="poi in pointsOfInterest">
      <LMarker
        :key="poi.id"
        :lat-lng="WKTPointToLatLng(poi.location.point)"
      >
        <LPopup>
          <component
            :is="sources[poi.source].renderer"
            v-bind="{ [sources[poi.source].objectName]: poi.object }"
          />
        </LPopup>
      </LMarker>
    </template>
  </Map>
</template>

<script>
  import { LMarker, LPopup } from 'vue2-leaflet'
  import Map from './Map.vue'
  import { WKTPointToLatLng } from './common'

  export default {
    name: 'GrouprisePointsOfInterest',
    components: { LMarker, LPopup, Map },
    props: {
      pointsOfInterest: {
        type: Array,
        required: true
      },
      height: {
        type: String,
        default: undefined
      }
    },
    data () {
      return {
        WKTPointToLatLng,
        sources: {
          group: {
            objectName: 'group',
            renderer: () => import('../content/group-preview.vue')
          }
        }
      }
    }
  }
</script>
