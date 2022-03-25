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

function selectTab (tabbed, tabIndex) {
  const tab = $(`.tabbed-tabs > li:nth-child(${tabIndex}) .tabbed-tab`, tabbed)
  const tabContent = $(`.tabbed-contents > li:nth-child(${tabIndex}) .tabbed-content`, tabbed)

  // disable all tabs and tab contents
  mapCall($$('.tabbed-tab', tabbed), removeClass, 'tabbed-tab-current')
  mapCall($$('.tabbed-content', tabbed), removeClass, 'tabbed-content-current')

  // enable selected tab and content
  addClass(tab, 'tabbed-tab-current')
  addClass(tabContent, 'tabbed-content-current')
}

// allow switching between tabs on click events and select the first tab (if it exists and if one is available)
export function configureTab (element_or_string, select_first_tab = true) {
  const selector = '.tabbed-tabs > li'
  const item_count = (
    (typeof element_or_string === 'string')
    ? document.querySelectorAll(element_or_string)
    : element_or_string
  ).querySelectorAll(selector).length

  if (select_first_tab && (item_count > 0)) {
    selectTab(element_or_string, 1)
  }
  return delegate(element_or_string, '.tabbed-tabs > li', 'click', (e) => {
    e.preventDefault()
    selectTab(element_or_string, index(e.delegateTarget))
  })
}

export default (opts) => {
  const iface = {}
  const tabbed = bel`<div class="tabbed">
    <ol class="tabbed-contents">${opts.tabs.map(renderTabContent)}</ol>
    <ol class="tabbed-tabs">${opts.tabs.map(renderTabLabel)}</ol>
</div>`

  const tabSelectListener = configureTab(tabbed, false)

  iface.remove = function () {
    tabSelectListener.destroy()
    remove(tabbed)
  }

  opts.tabs.length && selectTab(tabbed, 1)

  iface.el = tabbed

  return iface
}
