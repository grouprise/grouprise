import browser from 'bowser'
import bel from 'bel'
import delegate from 'delegate'

const isUnsupported = browser.isUnsupportedBrowser({
  msie: '11',
  firefox: '45',
  chrome: '49'
}, window.navigator.userAgent)

const dismissal = {
  key: 'browser-version-dismissed',
  isDismissed: function () {
    return window.localStorage.getItem(dismissal.key) === 'OK'
  },
  setDismissed: function () {
    window.localStorage.setItem(dismissal.key, 'OK')
  }
}

export default (el) => {
  const iface = {}

  if (!dismissal.isDismissed() && isUnsupported) {
    const disclaimer = bel`
            <div class="disclaimer disclaimer-info">
                        
                <button class="btn-text btn-text-light pull-right">
                    <i class="fa fa-times"></i>
                </button>
                
                <div class="container">
                    <p>
                        Entschuldige! Da wir Stadtgestalten als Projekt in unserer Freizeit entwickeln, können 
                        wir nicht so viel Rücksicht auf ältere Browser nehmen. Möglicherweise treten bei dir 
                        Probleme auf. <br>
                        Wir versuchen Firefox ab Version 45, Internet Explorer/Edge ab Version 11 und aktuelle
                        Chrome Versionen zu unterstützen.
                    </p>
                </div>
            </div>
        `

    const listener = delegate(disclaimer, 'button', 'click', () => {
      dismissal.setDismissed()
      iface.remove()
    })

    el.insertBefore(disclaimer, el.firstChild)

    iface.remove = function () {
      el.removeChild(disclaimer)
      listener.destroy()
    }
  } else {
    iface.remove = () => {}
  }

  return iface
}
