<template>
  <div class="form-group">
    <label class="control-label" for="event-time">Zeit</label>
    <div class="controls">
      <sg-configurator id="event-time" @save="propagate" @show="configure">
        <span slot="label">{{ label }}</span>
        <i slot="icon" class="fa fa-clock-o"></i>
        <span slot="title">
          Wann findet das Ereignis statt?
        </span>
        <sg-switch slot="modifiers" v-model="currentAllDay" trueLabel="Ja" falseLabel="Nein" label="Ganztägig"></sg-switch>
        <slot>
          <div class="datetime-row">
            <sg-datetime v-model="currentStartDate" :enableTime="!currentAllDay" :showLabels="true" dateLabel="Beginnt am" timeLabel="zu um"></sg-datetime>
            <div class="form-group" v-if="showDuration" key="duration">
              <label class="control-label">Dauer</label>
              <div class="controls">
                <sg-number-spinner v-model="duration" :step="1" :min="1" :label="durationLabel"></sg-number-spinner>
              </div>
            </div>
          </div>

          <div class="datetime-row" v-if="configurableEndDate">
            <sg-datetime v-model="currentEndDate" :enableTime="!currentAllDay" :showLabels="true" dateLabel="Endet am" timeLabel="zu um" :timeDefault="[23, 59, 59]"></sg-datetime>
          </div>

          <button type="button" class="btn btn-text" @click="configurableEndDate = true" v-if="!configurableEndDate">
            {{ currentAllDay ? 'Enddatum angeben' : 'Endzeit statt Dauer angeben' }}
          </button>
          <button type="button" class="btn btn-text" @click="configurableEndDate = false" v-else>
            {{ currentAllDay ? 'Enddatum entfernen' : 'Endzeit entfernen' }}
          </button>
        </slot>
      </sg-configurator>
    </div>
  </div>
</template>

<script>
  import moment from 'moment'
  import { inRange } from 'lodash'

  const calculateDuration = (start, end) => {
    const hours = Math.max(moment.duration(moment(end).diff(moment(start))).asHours(), 1)
    return [Math.round(hours), hours < 12 && inRange(hours / Math.round(hours) * 60, 58, 62)]
  }

  const label = (start, end, allDay) => {
    if(!start && !end) return "Zeit auswählen"

    if(!end) {
      if(allDay) return `Am ${moment(start).format('LL')}, ganztägig`
      else return `Am ${moment(start).format('LLL')} Uhr`
    } else {
      const sameDay = moment(start).isSame(end, "day")
      if(sameDay) {
        if(allDay) return `${moment(start).format('LL')}, ganztägig`
        else return `Am ${moment(start).format('LLL')} Uhr bis ${moment(end).format('LT')} Uhr`
      } else {
        if(allDay) return `Vom ${moment(start).format('LL')} bis ${moment(end).format('LL')}, ganztägig`
        else return `Vom ${moment(start).format('LLL')} Uhr bis ${moment(end).format('LLL')} Uhr`
      }
    }
  }

  export default {
    props: {
      start: {
        type: Date,
        default: null
      },
      end: {
        type: Date,
        default: null
      },
      allDay: {
        type: Boolean,
        default: false
      }
    },
    data() {
      return {
        configurableEndDate: false,
        duration: 1,
        currentStartDate: null,
        currentEndDate: null,
        currentAllDay: false
      }
    },
    computed: {
      showDuration() {
        return !this.configurableEndDate && !this.currentAllDay
      },
      durationLabel() {
        return this.duration === 1 ? 'Stunde' : 'Stunden'
      },
      finalEndDate() {
        const { configurableEndDate, duration, currentStartDate, currentEndDate, currentAllDay } = this

        if(configurableEndDate) {
          return moment(currentStartDate).isSame(currentEndDate, "day") && currentAllDay ? null : currentEndDate
        } else if(currentStartDate && currentAllDay) {
          return null
        } else if(currentStartDate && duration > 0) {
          const date = moment(currentStartDate)
          date.add(duration, "hours")
          return date.toDate()
        } else {
          return null
        }
      },
      label() {
        return label(this.start, this.end, this.allDay)
      }
    },
    methods: {
      propagate() {
        window.setTimeout(() => {
          this.$emit("change", {
            start: this.currentStartDate,
            end: this.finalEndDate,
            allDay: this.currentAllDay,
          })
        }, 0)
      },
      configure() {
        const [duration, showDuration] = calculateDuration(this.start, this.end)
        this.configurableEndDate = !showDuration
        this.duration = duration
      }
    },
    watch: {
      currentStartDate(currentStartDate) {
        // check if dates are valid and prefer start date when fixing
        const { configurableEndDate, currentEndDate, duration } = this
        if(configurableEndDate && currentEndDate && currentStartDate > currentEndDate ) {
          const momentDate = moment(currentStartDate)
          momentDate.add(duration, "hours")
          this.currentEndDate = momentDate.toDate()
        }
      },
      currentEndDate(currentEndDate) {
        // check if dates are valid and prefer end date when fixing
        const { configurableEndDate, currentStartDate, duration } = this
        if(configurableEndDate && currentEndDate && currentStartDate > currentEndDate) {
          const momentDate = moment(currentEndDate)
          momentDate.subtract(duration, "hours")
          this.currentStartDate = momentDate.toDate()
        }
      },
      configurableEndDate(isConfigurable) {
        if(!isConfigurable) {
          this.currentEndDate = null;
        } else {
          const momentDate = moment(this.currentStartDate)
          momentDate.add(this.duration, "hours")
          this.currentEndDate = momentDate.toDate()
        }
      }
    },
    created() {
      this.currentStartDate = this.start
      this.currentEndDate = this.end
      this.currentAllDay = this.allDay
      this.configure()
    }
  }
</script>
