function to_array(iterable) {
    return [].slice.call(iterable);
}

function $(selector, el = document) {
    return el.querySelector(selector);
}

function $$(selector, el = document) {
    return to_array(el.querySelectorAll(selector));
}

function replace(el_old, el_new) {
    el_old.parentNode.replaceChild(el_new, el_old);
    return el_new;
}

function index(el) {
    let index = 0;

    while(el = el.previousElementSibling) {
        index++;
    }

    return index;
}

function remove(el) {
    el.parentNode && el.parentNode.removeChild(el);
    return el;
}

function each(els, action, ...args) {
    return els.map((el) => {
        return action.apply(null, [].concat(el, args));
    });
}

function add_class(el, clazz) {
    el.classList.add(clazz);
    return el;
}

function toggle_class(el, clazz, force = false) {
    el.classList.toggle(clazz, force);
    return el;
}

function remove_class(el, clazz) {
    el.classList.remove(clazz);
    return el;
}

function get_attr(el, name, _default = void 0) {
    return el && el.hasAttribute(name) ? el.getAttribute(name) : _default;
}

function set_attr(el, name, value, append = false) {
    const attr_value = append ? get_attr(el, name, "") + " " + value : value;
    el.setAttribute(name, attr_value);
    return el;
}

function has_attr(el, name) {
    return el && el.hasAttribute(name);
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

export {
    $, $$,
    replace, index, remove,
    get_attr, has_attr, set_attr,
    add_class, remove_class, toggle_class,
    component, each,
};
