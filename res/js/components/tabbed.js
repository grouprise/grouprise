import bel from "bel";
import delegate from "delegate";
import { $, $$, index, each, remove, remove_class, add_class } from "../util/dom";

function tab_content(tab) {
    return bel`<li>
    <div class="tabbed-content">${tab.content}</div>
</li>`;
}

function tab_label(tab) {
    return bel`<li>
    <a href="#" class="tabbed-tab">${tab.label}</a>
</li>`;
}

export default (opts) => {
    const iface = {};
    const tabbed = bel`<div class="tabbed">
    <ol class="tabbed-contents">${opts.tabs.map(tab_content)}</ol>
    <ol class="tabbed-tabs">${opts.tabs.map(tab_label)}</ol>
</div>`;

    function select_tab(tab_index) {
        const tab = $(`.tabbed-tabs > li:nth-child(${tab_index}) .tabbed-tab`, tabbed);
        const tab_content = $(`.tabbed-contents > li:nth-child(${tab_index}) .tabbed-content`, tabbed);

        // disable all tabs and tab contents
        each($$(".tabbed-tab", tabbed), remove_class, "tabbed-tab-current");
        each($$(".tabbed-content", tabbed), remove_class, "tabbed-content-current");

        // enable selected tab and content
        add_class(tab, "tabbed-tab-current");
        add_class(tab_content, "tabbed-content-current");
    }

    const tab_select = delegate(tabbed, ".tabbed-tabs > li", "click", (e) => {
        e.preventDefault();
        select_tab(index(e.delegateTarget) + 1);
    });

    iface.remove = function() {
        tab_select.destroy();
        remove(tabbed);
    };

    opts.tabs.length && select_tab(1);

    iface.el = tabbed;

    return iface;
};
