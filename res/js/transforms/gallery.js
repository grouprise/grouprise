import Drop from "tether-drop";
import delegate from "delegate";
import qwest from "qwest";
import bel from "bel";

import { $, $$, replace } from "../util/dom";
import { evented_function } from "../util/events";
import editor_images from "../components/editor-image";

// create evented functions
const _replace = evented_function(replace);

function reload() {
    return qwest.get(location.href, null, { responseType: "document" })
        .then((xhr, doc) => {
            return Promise.resolve($(".gallery", doc));
        });
}

function create_editor(trigger) {
    const image_editor = editor_images({ tabs: { user: false, content: false }});
    const image_dialog = bel`<div class="editor-dialog">${image_editor.el}</div>`;

    const drop = new Drop({
        target: trigger,
        content: image_dialog,
        position: "bottom right",
    });

    const listener = delegate(trigger, "click", function(e) {
        e.preventDefault();
        drop.toggle();
    });

    return {
        emitter: image_editor.emitter,
        remove: function() {
            image_editor.remove();
            listener.destroy();
        }
    }
}

export default (el) => {
    const editor_add = $("[data-purpose='gallery-add']", el);

    if(!editor_add) {
        return;
    }

    const editor = create_editor(editor_add);
    editor.emitter.on("files:select", (files) => {
        reload().then((gallery) => {
            const old_gallery = $(".gallery", el);
            _replace(old_gallery, gallery);
        })
    })
}
