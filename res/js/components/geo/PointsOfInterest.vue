<template>
  <Map
    ref="map"
    :height="height"
    :maxBounds="maxBounds"
    @popupopen="isPopupOpen = true"
    @popupclose="isPopupOpen = false"
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
  import { isTruthy } from '../../util/strings'

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
      },
      restrictView: {
        type: String,
        default: undefined,
      }
    },
    data () {
      return {
        WKTPointToLatLng,
        isPopupOpen: false,
        sources: {
          group: {
            objectName: 'group',
            renderer: () => import('../content/group-preview.vue')
          }
        }
      }
    },
    computed: {
      /**
       * @returns {{options: {[p: string]: string}, type: string | null}}
       */
      viewRestriction () {
        const { restrictView } = this
        if (!restrictView) return { type: null, options: {} }
        const url = new URL(restrictView, 'file://')
        return {
          type: url.pathname.slice(1),
          options: Object.fromEntries(url.searchParams)
        }
      },
      maxBounds () {
        const { type, options } = this.viewRestriction
        if (!type) return null

        if (type === 'points') {
          if (this.pointsOfInterest.length === 0) return null
          if (this.isPopupOpen && isTruthy(options.disableForPopups)) return null
          let bounds = L.latLngBounds(this.pointsOfInterest.map((poi) => WKTPointToLatLng(poi.location.point)))
          if (options.pad) {
            bounds = bounds.pad(parseFloat(options.pad))
          }
          return bounds
        }

        throw new Error(`Unknown view restriction type: ${type}`)
      }
    }
  }
</script>
