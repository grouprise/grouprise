import closest from "closest";
import { keyPressed } from "luett";

const usage = `<span class='pull-right media-instruction'>
    <kbd>Shift</kbd> + <kbd>Enter</kbd> sendet das Formular ab
</span>`;

function on(el, event, listener) {
    el.addEventListener(event, listener, false);
    return () => el.removeEventListener(event, listener, false);
}

export default el => {
    el.insertAdjacentHTML("afterend", usage);

    const destroyInputListener = on(el, "keydown", keyPressed(13, { shiftKey: true }, event => {
        event.preventDefault();
        closest(el, "form").dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
    }));

    return {
        el,
        remove: () => {
            destroyInputListener();
        }
    }
};
