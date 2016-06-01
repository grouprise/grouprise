function $(selector, el = document) {
    return el.querySelector(selector);
}

function $$(selector, el = document) {
    return [].slice.call(el.querySelectorAll(selector));
}

function component(name, init) {
    function parse_conf(el) {
        const default_conf = {};

        try {
            const conf = JSON.parse(el.getAttribute("data-component-conf"));
            return conf || default_conf;
        } catch(e) {
            return default_conf;
        }
    }

    return $$(`[data-component~="${name}"]`)
        .map((el, index) => {
            const def = el.getAttribute("data-component").split(" ");

            const options = {
                index,
                conf: parse_conf(el),
                is_type(type) {
                    return def.indexOf(`${name}-${type}`) !== -1;
                }
            };

            return init(el, options);
        });
}

export { $, $$, component };
