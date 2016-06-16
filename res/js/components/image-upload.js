import Dropzone from "dropzone";
import qwest from "qwest";
import { $ } from "../util/dom";
import { success  } from "../util/notify";

Dropzone.autoDiscover = false;

export default function image_upload(el, opts) {
    if(el.tagName !== "FORM") {
        throw new Error("image-upload component is only allowed on forms");
    }
    
    if(typeof opts.conf.content !== "number") {
        throw new Error("missing content id");
    }

    const update = opts.conf.update ?
        typeof opts.conf.update === "string"
            ? [opts.conf.update] : opts.conf.update
            : [];
    
    el.classList.add("dropzone");
    el.innerHTML = "";
    let counter = 0;
    
    const dropzone = new Dropzone(el, {
        url: "/stadt/api/images/",
        acceptedFiles: "image/*",
        dictDefaultMessage: "Klick oder zieh Bilder hierhin"
    });

    dropzone.on("sending", (file, xhr, form_data) => {
        form_data.set("content", opts.conf.content);
        form_data.set("weight", 0);
        counter++;
    });

    dropzone.on("success", (file) => {
        dropzone.removeFile(file);
    });

    dropzone.on("queuecomplete", () => {
        success(`${counter} Bild${counter == "1" ? "" : "er"} wurden hochgeladen`);
        counter = 0;

        if(update.length) {
            qwest.get(location.href, null, { responseType: "document" })
                .then((xhr, doc) => {
                    update.forEach((selector) => opts.conf.replace($(selector), $(selector, doc)));
                });
        }
    });

    return dropzone;
};
