<template>
  <div class="datetime">
    <div class="datetime-calendar" ref="calendar"></div>
    <div class="form-group datetime-date">
      <label class="control-label" v-if="showLabels">{{ dateLabel }}</label>
      <div class="controls">
        <input type="text" class="form-control form-control-icon" v-model="date" ref="date" @focus="isEditing = true">
      </div>
    </div>
    <transition name="fade">
      <div class="form-group datetime-time" v-if="enableTime">
        <label class="control-label" v-if="showLabels">{{ timeLabel }}</label>
        <div class="controls">
          <input type="text" class="form-control form-control-icon" v-model="time" ref="time"
                 placeholder="z.B: 12:30" pattern="^([0[0-9]|1[0-9]|2[0-3]):?[0-5][0-9]$"
                 @focus="isEditing = true" @blur="guessTime" @wheel.prevent="scrollTime">
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
  import { throttle } from 'lodash'
  import moment from 'moment'
  import date from '../../transforms/date'

  const ensureArray = value => typeof value === 'string' ? [value] : value;
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
    return momentDate ? momentDate.format(finalFormat) : ""
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
        default: () => "L"
      },
      timeFormat: {
        type: [String, Array],
        default: () => ["HH:mm", "HH:m", "H:mm", "H:m", "HHmm", "Hmm", "HHm", "HH", "H"]
      },
      dateLabel: {
        type: String,
        default: "Datum"
      },
      timeLabel: {
        type: String,
        default: "Zeit"
      },
      timeStep: {
        type: Number,
        default: 30,
      },
      disableDates: {
        type: Array,
        default: () => []
      },
    },
    data() {
      return {
        date: null,
        time: '12:00',
        datePicker: null,
        currentValue: null,
        isEditing: false
      }
    },
    computed: {
      finalValue() {
        const {enableTime, date, time, dateFormat, timeFormat} = this
        const parsedDate = checkDate(date, dateFormat)
        const parsedTime = checkDate(time, timeFormat)

        if (parsedDate) {
          let timeOffset

          if (!enableTime) {
            timeOffset = this.timeDefault
          } else if (enableTime && parsedTime) {
            timeOffset = ["hour", "minute", "second"].map(u => parsedTime.get(u))
          } else {
            return null
          }

          parsedDate.set("hour", timeOffset[0])
          parsedDate.set("minute", timeOffset[1])
          parsedDate.set("second", timeOffset[2])

          return parsedDate.toDate()
        }

        return null
      }
    },
    methods: {
      setFromSource() {
        if (this.isEditing) return

        this.currentValue = this.value || null
        this.date = format(this.currentValue, this.dateFormat)
        this.time = format(this.currentValue, this.timeFormat) || this.time

        if (this.$refs.date && this.$refs.date._flatpickr) {
          this.$refs.date._flatpickr.setDate(this.currentValue)
        }
      },
      guessTime(event) {
        const {timeFormat} = this
        const el = event.target
        const time = el.value
        const parsedTime = checkDate(time, timeFormat)

        if (parsedTime) {
          this.time = format(parsedTime, timeFormat)
        }
      },
      increaseTime(step) {
        const el = this.$refs.time
        const {timeFormat} = this
        const parsedTime = checkDate(el.value, timeFormat)
        if (parsedTime) {
          this.time = format(parsedTime.add(step, 'minutes'), timeFormat)
        }
      },
      scrollTime: throttle(function (event) {
        if (Math.abs(event.deltaY) >= 20) {
          this.increaseTime(this.timeStep * (event.deltaY < 0 ? -1 : 1))
        }
      }, 35, {trailing: false}),
    },
    watch: {
      value() { setTimeout(() => this.setFromSource(), 0) },
      finalValue(date) {
        setTimeout(() => this.$emit("input", date), 0)
      }
    },
    created() {
      this.setFromSource()
    },
    mounted() {
      this.datePicker = date(this.$refs.date, {
        disable: this.disableDates,
        appendTo: this.$refs.calendar,
        static: true,
      })
    },
    beforeDestroy() {
      this.datePicker.remove()
    }
  }
</script>
