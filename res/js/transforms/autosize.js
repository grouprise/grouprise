import autosize from 'autosize'
import { setAttr } from 'luett'

export default (el, opts) => {
  if (opts.conf.rows) {
    setAttr(el, 'rows', opts.conf.rows)
  }

  autosize(el)

  return {
    remove() {
      autosize.destroy(el)
    }
  }
}
