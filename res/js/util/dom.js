function $(selector, el = document) {
    return el.querySelector(selector);
}

function $$(selector, el = document) {
    return [].slice.call(el.querySelectorAll(selector));
}

function component(name, init) {
    return $$(`[data-component="${name}"]`).map(init);
}

export { $, $$, component };
