import autosize from 'autosize'
import { setAttr } from 'luett'

export default el => {
  setAttr(el, 'rows', 1)
  autosize(el)

  return {
    remove() {
      autosize.destroy(el)
    }
  }
}
