let rowIndex = -1

export default {
  model: {
    prop: 'answers'
  },
  props: {
    answers: Array
  },
  data () {
    return {
      newRowIndex: -1
    }
  },
  methods: {
    removeRow (index) {
      this.answers.splice(index, 1)
    },
    newRow (data) {
      this.answers.push({
        rowIndex: rowIndex--,
        value: data
      })
    }
  }
}
