import { $, $$, index, mapCall, remove, removeClass, addClass } from 'luett'
import bel from 'bel'
import delegate from 'delegate'

function renderTabContent (tab) {
  return bel`<li>
    <div class="tabbed-content">${tab.content}</div>
</li>`
}

function renderTabLabel (tab) {
  return bel`<li>
    <a href="#" class="tabbed-tab">${tab.label}</a>
</li>`
}

export default (opts) => {
  const iface = {}
  const tabbed = bel`<div class="tabbed">
    <ol class="tabbed-contents">${opts.tabs.map(renderTabContent)}</ol>
    <ol class="tabbed-tabs">${opts.tabs.map(renderTabLabel)}</ol>
</div>`

  function selectTab (tabIndex) {
    const tab = $(`.tabbed-tabs > li:nth-child(${tabIndex}) .tabbed-tab`, tabbed)
    const tabContent = $(`.tabbed-contents > li:nth-child(${tabIndex}) .tabbed-content`, tabbed)

        // disable all tabs and tab contents
    mapCall($$('.tabbed-tab', tabbed), removeClass, 'tabbed-tab-current')
    mapCall($$('.tabbed-content', tabbed), removeClass, 'tabbed-content-current')

        // enable selected tab and content
    addClass(tab, 'tabbed-tab-current')
    addClass(tabContent, 'tabbed-content-current')
  }

  const tabSelectListener = delegate(tabbed, '.tabbed-tabs > li', 'click', (e) => {
    e.preventDefault()
    selectTab(index(e.delegateTarget) + 1)
  })

  iface.remove = function () {
    tabSelectListener.destroy()
    remove(tabbed)
  }

  opts.tabs.length && selectTab(1)

  iface.el = tabbed

  return iface
}
