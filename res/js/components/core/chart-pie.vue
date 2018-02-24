<template>
  <svg viewBox="-1 -1 2 2" class="chart chart-pie" :style="style">
    <g transform="rotate(-90)">
      <g class="chart-arc" v-for="(item, index) in data">
        <title v-if="item.title">{{ item.title }}</title>
        <path :d="calculateArc(item, index)" :class="item.classes" />
      </g>
    </g>
  </svg>
</template>

<script>
  import { range } from 'lodash'

  function getCoordinatesForPercent (percent) {
    const x = Math.cos(2 * Math.PI * percent / 100).toFixed(5)
    const y = Math.sin(2 * Math.PI * percent / 100).toFixed(5)

    return [x, y]
  }

  function calculateArc (start, end) {
    const [startX, startY] = getCoordinatesForPercent(start)
    const [endX, endY] = getCoordinatesForPercent(end)
    const largeArcFlag = end - start > 50 ? 1 : 0
    return `M ${startX} ${startY} A 1 1 0 ${largeArcFlag} 1 ${endX} ${endY} L 0 0`
  }

  export default {
    props: {
      data: Array,
      size: String
    },
    computed: {
      style () {
        const size = this.size ? this.size : '3rem'
        return {
          width: size,
          height: size
        }
      }
    },
    methods: {
      calculateArc (item, index) {
        const startPercentage = range(0, index)
          .reduce((result, index) => result + this.data[index].percentage, 0)
        const endPercentage = index + 1 === this.data.length
          ? 100 : startPercentage + item.percentage
        return calculateArc(startPercentage, endPercentage)
      }
    }
  }
</script>

<documentation>
  helpful article: https://hackernoon.com/a-simple-pie-chart-in-svg-dbdd653b6936
</documentation>
