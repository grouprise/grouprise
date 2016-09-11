function attach_and_run(target, event, listener) {
    event.split(" ").forEach((event) => event && target.addEventListener(event, listener, false));
    listener.call(target);
}

export default (el, conf = {}) => {
    const target = conf.target || el;

    function set_changed_states() {
        const is_filled =  el.value.trim() !== "";
        target.classList.toggle("input-filled", is_filled);
        target.classList.toggle("input-empty", !is_filled);
    }

    function set_focus_states() {
        const is_focused = document.activeElement === el;

        target.classList.toggle("input-focused", is_focused);
        target.classList.toggle("input-blurred", !is_focused);
    }

    function set_type() {
        target.classList.toggle(`input-type-${el.tagName.toLowerCase()}`, true);
    }

    attach_and_run(el, "input change", set_changed_states);
    attach_and_run(el, "focus blur", set_focus_states);

    set_type();
};
