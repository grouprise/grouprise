// TODO https://github.com/NextStepWebs/simplemde-markdown-editor/issues/150
import SimpleMDE from "simplemde/dist/simplemde.min";

export default (el) => new SimpleMDE({
    element: el,
    parsingConfig: {
        allowAtxHeaderWithoutSpace: true,
        strikethrough: false,
    },
    renderingConfig: {
        singleLineBreaks: false,
    },
    shortcuts: {
        "toggleBold": "Shift-Cmd-F",
    },
    spellChecker: false,
    status: false,
    /*
    toolbar: [
        {
            name: "bold",
            action: SimpleMDE.toggleBold,
            className: "fa fa-bold",
            title: "Fett",
        },
        {
            name: "guide",
            action: "https://simplemde.com/markdown-guide",
            className: "fa fa-question-circle",
            title: "Hilfe",
        },
    ],
    */
});
