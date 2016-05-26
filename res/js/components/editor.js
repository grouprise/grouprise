// TODO https://github.com/NextStepWebs/simplemde-markdown-editor/issues/150
import SimpleMDE from "simplemde/dist/simplemde.min";

export default (el) => new SimpleMDE({
    element: el,
    parsingConfig: {
        allowAtxHeaderWithoutSpace: true,
        strikethrough: false,
    },
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
            action: SimpleMDE.drawImage,
            className: "fa fa-picture-o",
            title: "Bild",
        },
        "|",
        {
            name: "guide",
            action: "https://simplemde.com/markdown-guide",
            className: "fa fa-question-circle",
            title: "Hilfe",
        },
    ],
});
