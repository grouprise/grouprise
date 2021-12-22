import '../../../css/components/leaflet.less'

import L, { featureGroup, latLng, marker } from 'leaflet'

delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
})

export function WKTPointToLatLng (point) {
  const { latitude, longitude } = point.match(/POINT \((?<latitude>-?\d+(?:\.\d*)?) (?<longitude>-?\d+(?:\.\d*)?)\)/).groups
  return latLng(parseFloat(latitude), parseFloat(longitude))
}

export function LatLngToWKTPoint (latLng) {
  return `POINT (${latLng.lat} ${latLng.lng})`
}

export function LatLngToBounds (...points) {
  return featureGroup(points.map(p => marker(p))).getBounds()
}
