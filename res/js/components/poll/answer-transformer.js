import moment from 'moment'
import { getTimeFormat } from '../../util/dom'

export default (pollTypeAdapter, formsetAdapter) => {
  const pollType = pollTypeAdapter.get().value
  return {
    get () {
      return formsetAdapter.rows
        .filter(row => !row.delete)
        .map({
          simple: row => {
            return {
              rowIndex: row.index,
              value: {
                title: row.field('title').value
              }
            }
          },
          event: row => {
            const timeField = row.field('time')
            const timeUntilField = row.field('until_time')

            const time = timeField.value
              ? moment(timeField.value, getTimeFormat(timeField), true)
              : moment()
            const timeUntil = timeUntilField.value
              ? moment(timeUntilField.value, getTimeFormat(timeUntilField), true)
                  .diff(time, 'hours')
              : null
            return {
              rowIndex: row.index,
              value: {
                start: time.toDate(),
                duration: timeUntil !== null ? timeUntil : null
              }
            }
          }
        }[pollType])
    },
    set (rows) {
      const rowIndices = rows.map(row => row.rowIndex)
      const intactRows = rowIndices.map(index => index)

      // delete missing rows
      formsetAdapter.rows.forEach(row => {
        if (!intactRows.includes(row.index)) {
          row.delete = true
        }
      })

      // transform row data
      const rowData = rows.map({
        simple: row => ({
          rowIndex: row.rowIndex,
          value: formsetAdapter.dataArrayFromObject(row.value)
        }),
        event: row => ({
          rowIndex: row.rowIndex,
          value: formsetAdapter.dataArrayFromObject({
            time: moment(row.value.start).format(String(getTimeFormat)),
            until_time: row.value.duration
              ? moment(row.value.start).add(row.value.duration, 'h').format(String(getTimeFormat))
              : ''
          })
        })
      }[pollType])

      // create new rows
      rowData
        .filter(row => row.rowIndex < 0)
        .forEach(row => formsetAdapter.templateRow.createRow(row.value))

      // update existing rows
      rowData
        .filter(row => row.rowIndex >= 0)
        .forEach(row => formsetAdapter.findRow(row.rowIndex).setData(row.value))
    }
  }
}
