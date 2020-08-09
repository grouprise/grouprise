<template>
  <div class="datetime">
    <div
      ref="calendar"
      class="datetime-calendar"
    />
    <div
      ref="dateFieldGroup"
      class="form-group datetime-date"
    >
      <label
        v-if="showLabels"
        class="control-label"
        :for="dateFieldId"
      >{{ dateLabel }}</label>
      <div class="controls">
        <input
          :id="dateFieldId"
          ref="date"
          v-model.lazy="date"
          type="text"
          class="form-control form-control-icon"
          @focus="isEditing = true"
          @blur="isEditing = false"
          @wheel="scrollDate"
        >
      </div>
    </div>
    <transition name="fade">
      <div
        v-if="enableTime"
        ref="timeFieldGroup"
        class="form-group datetime-time"
      >
        <label
          v-if="showLabels"
          class="control-label"
          :for="timeFieldId"
        >{{ timeLabel }}</label>
        <div class="controls">
          <input
            :id="timeFieldId"
            ref="time"
            type="text"
            class="form-control form-control-icon"
            pattern="^(0[0-9]|1[0-9]|2[0-3]):?[0-5][0-9]$"
            :placeholder="timePlaceholder"
            :value="time"
            @focus="isEditing = true"
            @change="guessTime"
            @wheel="scrollTime"
          >
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
  import randomId from 'random-id'
  import { throttle } from 'lodash'
  import moment from 'moment'
  import date from '../../transforms/date'
  import input from '../../transforms/input'

  const ensureArray = value => typeof value === 'string' ? [value] : value
  const checkDate = (date, formats) => {
    const validFormats = ensureArray(formats).filter(format => moment(date, format, true).isValid())

    if (validFormats.length > 0) {
      const format = validFormats[0]
      return moment(date, format)
    }

    return null
  }
  const format = (date, format) => {
    const formats = ensureArray(format)
    const finalFormat = formats[0]
    const momentDate = checkDate(date, formats)
    return momentDate ? momentDate.format(finalFormat) : ''
  }
  const wheelListener = callback => {
    const throttledCallback = throttle(callback, 35, { trailing: false })
    return function (event) {
      if (document.activeElement === event.target && Math.abs(event.deltaY) >= 2) {
        event.preventDefault()
        throttledCallback.call(this, event, event.deltaY < 0 ? 1 : -1)
      }
    }
  }

  export default {
    props: {
      enableTime: {
        type: Boolean,
        default: true
      },
      timeDefault: {
        type: Array,
        default: () => [0, 0, 0]
      },
      showLabels: {
        type: Boolean,
        default: false
      },
      value: {
        type: Date
      },
      dateFormat: {
        type: [String, Array],
        default: () => 'L'
      },
      timeFormat: {
        type: [String, Array],
        default: () => ['HH:mm', 'HH:m', 'H:mm', 'H:m', 'HHmm', 'Hmm', 'HHm', 'HH', 'H']
      },
      timePlaceholder: String,
      dateLabel: {
        type: String,
        default: 'Datum'
      },
      timeLabel: {
        type: String,
        default: 'Zeit'
      },
      timeStep: {
        type: Number,
        default: 15
      },
      disableDates: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        date: null,
        time: '12:00',
        datePicker: null,
        dateField: null,
        timeField: null,
        currentValue: null,
        isEditing: false,
        id: randomId(20, 'a')
      }
    },
    computed: {
      dateFieldId () {
        return `${this.id}-date`
      },
      timeFieldId () {
        return `${this.id}-time`
      },
      finalValue () {
        const {enableTime, date, time, dateFormat, timeFormat} = this
        const parsedDate = checkDate(date, dateFormat)
        const parsedTime = checkDate(time, timeFormat)

        if (parsedDate) {
          let timeOffset

          if (!enableTime) {
            timeOffset = this.timeDefault
          } else if (enableTime && parsedTime) {
            timeOffset = ['hour', 'minute', 'second'].map(u => parsedTime.get(u))
          } else {
            return null
          }

          parsedDate.set('hour', timeOffset[0])
          parsedDate.set('minute', timeOffset[1])
          parsedDate.set('second', timeOffset[2])

          return parsedDate.toDate()
        }

        return null
      }
    },
    methods: {
      setFromSource () {
        if (this.isEditing) return

        this.currentValue = this.value || null
        this.date = format(this.currentValue, this.dateFormat)
        this.time = format(this.currentValue, this.timeFormat) || this.time

        if (this.$refs.date && this.$refs.date._flatpickr) {
          this.$refs.date._flatpickr.setDate(this.currentValue)
        }
      },
      guessTime (event) {
        const {timeFormat} = this
        const el = event.target
        const time = el.value
        const parsedTime = checkDate(time, timeFormat)

        this.isEditing = false

        if (parsedTime) {
          this.time = format(parsedTime, timeFormat)
        }
      },
      increaseTime (step) {
        const el = this.$refs.time
        const {timeFormat} = this
        const parsedTime = checkDate(el.value, timeFormat)
        if (parsedTime) {
          this.time = format(parsedTime.add(step, 'minutes'), timeFormat)
        }
      },
      increaseDate (step) {
        const el = this.$refs.date
        const {dateFormat} = this
        const parsedTime = checkDate(el.value, dateFormat) || moment()
        if (parsedTime) {
          this.date = format(parsedTime.add(step, 'days'), dateFormat)
        }
      },
      scrollDate: wheelListener(function (event, direction) {
        this.increaseDate(direction)
      }),
      scrollTime: wheelListener(function (event, direction) {
        this.increaseTime(this.timeStep * direction)
      })
    },
    watch: {
      value () {
        setTimeout(() => this.setFromSource(), 0)
      },
      finalValue (date) {
        setTimeout(() => this.$emit('input', date), 0)
      },
      enableTime (enable) {
        if (enable) {
          this.timeField = input(this.$refs.time, {
            conf: { target: () => this.$refs.timeFieldGroup }
          })
        } else if (this.timeField) {
          this.timeField.remove()
          this.timeField = null
        }
      }
    },
    created () {
      this.setFromSource()
    },
    mounted () {
      this.dateField = input(this.$refs.date, {
        conf: { target: () => this.$refs.dateFieldGroup }
      })
      if (this.enableTime) {
        this.timeField = input(this.$refs.time, {
          conf: { target: () => this.$refs.timeFieldGroup }
        })
      }
      this.datePicker = date(this.$refs.date, {
        disable: this.disableDates,
        appendTo: this.$refs.calendar,
        static: true
      })
    },
    beforeDestroy () {
      this.datePicker.remove()
      this.dateField.remove()
      if (this.timeField) this.timeField.remove()
    }
  }
</script>
