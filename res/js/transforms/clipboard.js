import { remove } from 'luett'
import Clipboard from 'clipboard'
import browser from 'bowser'
import { success, danger } from '../util/notify'

const isUnsupported = browser.isUnsupportedBrowser({
  msie: '9',
  firefox: '41',
  chrome: '42',
  edge: '12',
  opera: '29',
  safari: '10'
}, window.navigator.userAgent)

export default (el, opts) => {
  if (isUnsupported) {
    remove(el)
    return {
      remove () {}
    }
  }

  const clipboard = new Clipboard(el, {
    text: opts.conf.text
  })

  clipboard.on('success', function () {
    success('URL wurde kopiert')
  })

  clipboard.on('error', function () {
    danger('URL konnte nicht kopiert werden. Bitte markiere den Text und kopiere ihn per Hand.')
  })

  return {
    remove () {
      clipboard.off()
      clipboard.destroy()
    }
  }
}
