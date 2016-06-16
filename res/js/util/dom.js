function $(selector, el = document) {
    return el.querySelector(selector);
}

function $$(selector, el = document) {
    return [].slice.call(el.querySelectorAll(selector));
}

function replace(el_old, el_new) {
    el_old.parentNode.replaceChild(el_new, el_old);
    return el_new;
}

function component(name, init, opts = {}) {
    function parse_conf(el) {
        const default_conf = {};

        try {
            const conf = JSON.parse(el.getAttribute("data-component-conf"));
            return conf || default_conf;
        } catch(e) {
            return default_conf;
        }
    }
    
    opts = opts instanceof HTMLElement ? { root: opts } : opts;

    return $$(`[data-component~="${name}"]`, opts.root || document)
        .filter((el) => !el.hasAttribute("data-component-ready"))
        .map((el, index) => {
            const def = el.getAttribute("data-component").split(" ");
            const conf = Object.assign({}, init.DEFAULTS || {}, opts.conf || {}, parse_conf(el));

            const options = {
                index, conf,
                is_type(type) {
                    return def.indexOf(`${name}-${type}`) !== -1;
                }
            };

            const component = init(el, options);
            el.setAttribute("data-component-ready", "");
            return component;
        });
}

export { $, $$, component, replace };
