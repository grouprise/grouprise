import bel from "bel";
import EventEmitter from "eventemitter3";

import { $, get_attr, remove } from "../util/dom";
import { get as get_images, create as create_image } from "../adapters/image";
import pickii from "./pickii";
import file_picker from "./file-picker";
import tabbed from "./tabbed";

const emitter = new EventEmitter();
const content_id = get_attr($("[name='content_id']"), "value", false);

function upload(files) {
    const uploader = create_image({ content_id });
    const uploads = files.map((file) => {
        return uploader({
            content: file
        });
    });

    return Promise.all(uploads);
}

function dummy_adapter() {
    return Promise.resolve([]);
}

function create_file_picker() {
    return file_picker({
        accept: "image/*;capture=camera",
        multiple: true,
        callback: (files) => {
            upload(files)
                .then((files) => {
                    emitter.emit("files:select", files)
                    emitter.emit("files:add", files)
                });
        },
        trigger: bel`<button type="button" class="btn btn-link btn-sm">
    <i class="sg sg-add"></i> Hinzufügen
</button>`
    });
}

function create_content_image_view() {
    return pickii({
        emit: emitter.emit.bind(emitter),
        adapter: content_id ? get_images({
            filters: { content: content_id }
        }) : dummy_adapter
    });
}

function create_user_image_view() {
    return pickii({
        emit: emitter.emit.bind(emitter),
        adapter: window.gestalt.id ? get_images({
            filters: { creator: window.gestalt.id }
        }) : dummy_adapter
    })
}

function created_tabbed() {
    const content_image_view = create_content_image_view();
    const user_image_view = create_user_image_view();

    emitter.on("files:add", function() {
        content_image_view.refresh();
        user_image_view.refresh();
    });

    return tabbed({
        tabs: [
            {
                content: content_image_view.el,
                label: bel`<span>Beitragsbilder</span>`
            },
            {
                content: user_image_view.el,
                label: bel`<span>Deine Bilder</span>`
            }
        ]
    });
}


export default (opts) => {
    const iface = {};
    const image_editor = bel`<div class="editor-images">
    <div class="btn-toolbar btn-toolbar-spread">
        <h3>Bilder</h3>
        ${create_file_picker().el}
    </div>
    ${created_tabbed().el}
</div>`;

    iface.remove = function() {
        remove(image_editor);
    };

    iface.emitter = emitter;
    iface.el = image_editor;

    return iface;
};
