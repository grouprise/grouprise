import { $ } from "luett";

function on(el, event, listener, capture = false) {
    el.addEventListener(event, listener, capture);
    return () => el.removeListener(event, listener, capture);
}

function create_listener(el, state) {
    const set = (value) => function() { state.is_current = value };

    const set_active = on(el, "mouseenter", set(true));
    const set_inactive = on(el, "mouseleave", set(false));

    return () => {
        set_active();
        set_inactive();
    }
}

export default (el, opts) => {
    const target = $(opts.conf.target);
    const state = { is_current: false, is_active: !!opts.conf.is_active };

    const source_listener = create_listener(el, state);
    const target_listener = create_listener(target, state);
    const trigger_listener = on(el, "click", () => { state.is_active = !state.is_active; });
    const doc_listener = on(document.documentElement, "click", () => {
        if(!state.is_current && state.is_active) {
            el.click();
        }
    });

    return {
        remove: () => {
            source_listener();
            target_listener();
            trigger_listener();
            doc_listener();
        }
    }
}
