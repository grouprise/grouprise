import bel from "bel";
import { remove } from "../util/dom";

export default (opts) => {
    const iface = {};
    const input = bel`<input type="file" style=${{display: "none"}} onchange=${(e) => opts.callback([].slice.call(e.target.files))} />`;

    if(opts.accept) {
        input.setAttribute("accept", opts.accept);
    }

    if(opts.multiple) {
        input.setAttribute("multiple", "");
    }

    opts.trigger.onclick = (e) => {
        e.preventDefault();
        input.click();
    };

    const picker = bel`<div>${opts.trigger}${input}</div>`;

    iface.remove = function() {
        remove(picker);
    };

    iface.el = picker;

    return iface;
};
