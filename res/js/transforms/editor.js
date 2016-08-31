import SimpleMDE from "simplemde";
import Drop from "tether-drop";
import bel from "bel";

import editor_images from "../components/editor-image";

const image_editor = editor_images();
const image_dialog = bel`<div class="editor-dialog">${image_editor.el}</div>`;

export default (el, opts) => {
    const editor =  new SimpleMDE({
        autoDownloadFontAwesome: false,
        element: el,
        forceSync: true,
        parsingConfig: {
            allowAtxHeaderWithoutSpace: true,
            strikethrough: false,
        },
        promptTexts: {
            link: "Adresse des Linkziels (URL):",
            image: "Adresse des Bildes (URL):"
        },
        promptURLs: true,
        shortcuts: {
            "toggleBold": "Shift-Ctrl-F",
            "toggleItalic": "Ctrl-I",
            "undo": "Ctrl-Z",
            "redo": "Ctrl-Y",
            "toggleUnorderedList": "Shift-F12",
            "toggleOrderedList": "F12",
            "toggleHeading2": "Ctrl-2",
            "toggleHeading3": "Ctrl-3",
        },
        spellChecker: false,
        status: false,
        toolbar: [
            {
                name: "undo",
                action: SimpleMDE.undo,
                className: "fa fa-undo no-disable",
                title: "Rückgängig"
            },
            {
                name: "redo",
                action: SimpleMDE.redo,
                className: "fa fa-repeat no-disable",
                title: "Wiederholen"
            },
            "|",
            {
                name: "italic",
                action: SimpleMDE.toggleItalic,
                className: "fa fa-italic",
                title: "Kursiv",
            },
            {
                name: "bold",
                action: SimpleMDE.toggleBold,
                className: "fa fa-bold",
                title: "Fett",
            },
            "|",
            {
                name: "unordered-list",
                action: SimpleMDE.toggleUnorderedList,
                className: "fa fa-list-ul",
                title: "Einfache Liste",
            },
            {
                name: "ordered-list",
                action: SimpleMDE.toggleOrderedList,
                className: "fa fa-list-ol",
                title: "Nummerierte Liste",
            },
            "|",
            {
                name: "heading-2",
                action: SimpleMDE.toggleHeading2,
                className: "fa fa-header",
                title: "Überschrift"
            },
            {
                name: "heading-3",
                action: SimpleMDE.toggleHeading3,
                className: "fa fa-header fa-header-x fa-header-2",
                title: "Unterüberschrift"
            },
            "|",
            {
                name: "link",
                action: SimpleMDE.drawLink,
                className: "fa fa-link",
                title: "Link/Verweis",
            },
            {
                name: "image",
                className: "fa fa-picture-o",
                title: "Bild",
            },
            "|",
            {
                name: "guide",
                action: "/stadt/markdown",
                className: "fa fa-question-circle",
                title: "Möglichkeiten der Textauszeichnung",
            },
        ],
    });

    const drop = new Drop({
        target: editor.toolbarElements["image"],
        content: image_dialog,
        position: "bottom left",
        openOn: "click"
    });

    image_editor.emitter.on("files:select", (files) => {
        const code = files.map((file) => {
            return `![${file.label}](${file.content})`;
        }).join("\n");

        editor.codemirror.doc.replaceSelection(code);
        drop.close();
    });

    return editor;
}
